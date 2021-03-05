#! usr/bin/env python3
import asyncio
import logging
import pprint
import time
from datetime import datetime

import asyncpraw
import asyncprawcore
import discord
from discord.ext import commands, tasks

import commands as bot_commands
from core.config import (
    DEXTER_ADMIN_ROLE_ID,
    DEXTER_CHANNEL_LOGS_ID,
    CLIENT_ID,
    CLIENT_SECRET,
    DATABASE_NAME,
    DEXTER_DISCORD_GUILD_ID,
    DEXTER_ID,
    DISCORD_TOKEN,
    REDDIT_PASSWORD,
    REDDIT_USER,
)
from db.mongodb import get_database
from db.mongodb_init import close_mongo_connection, connect_to_mongo

pp = pprint.PrettyPrinter(indent=4)

logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.INFO)

illegal_char_list = [".", ",", "!", "?", "[", "]"]


reddit = asyncpraw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent="Reddit Job Finder Discord Bot",
    username=REDDIT_USER,
    password=REDDIT_PASSWORD,
)

client = commands.Bot(command_prefix="$sudo", help_command=None)


@client.event
async def on_ready():
    connect_to_mongo()
    print(f"{client.user} is connected to the following guild:\n")
    for guild in client.guilds:
        print(f"{guild.name}(id: {guild.id})")


def build_discord_embed_message(submission, keyword):
    title = submission.title
    if len(title) > 256:
        title = submission.title[:252] + "..."
    description = submission.selftext
    if len(description) > 2048:
        description = submission.selftext[:2044] + "..."
    embed = discord.Embed(
        title=f"{title}",
        color=discord.Colour(0x82DE09),
        url=f"https://www.reddit.com{submission.permalink}",
        description=f"{description}",
    )
    embed.set_author(name=f"{submission.author.name}")
    embed.set_footer(
        text=f"Subreddit {submission.subreddit_name_prefixed} "
        f'| {time.strftime("%a %b %d, %Y at %H:%M:%S", time.gmtime(submission.created_utc))}'
    )
    try:
        embed.set_thumbnail(url=f'{submission.preview["images"][0]["source"]["url"]}')
    except AttributeError:
        pass
    embed.add_field(name="#️⃣", value=f"{keyword.capitalize()}", inline=False)
    embed.add_field(name="👍", value=f"{submission.ups}", inline=True)
    embed.add_field(name="👎", value=f"{submission.downs}", inline=True)
    embed.add_field(name="💬", value=f"{submission.num_comments}", inline=True)

    return embed


def build_discord_embed_logs(e):
    embed = discord.Embed(
        title=f"🚑 {e}",
        color=discord.Colour(0xE74C3C),
        description=f"{e.__doc__}",
    )

    return embed


async def send_discord_message(submission, keyword, channel_id):
    channel = client.get_channel(channel_id)
    await channel.send(embed=build_discord_embed_message(submission, keyword))
    # print(f'Link : https://www.reddit.com{submission.permalink}')


async def mention_admin_in_case_of_exceptions(e):
    channel = client.get_channel(DEXTER_CHANNEL_LOGS_ID)
    guild = client.get_guild(id=DEXTER_DISCORD_GUILD_ID)
    admin = discord.utils.get(guild.roles, id=int(DEXTER_ADMIN_ROLE_ID))
    await channel.send(
        f"{admin.mention} I'm sick, please help me!",
        embed=build_discord_embed_logs(e),
    )


async def search_for_illegal_words_and_trigger_message_sending(
    word, keyword_job, submission, sent_submission_id_list, conn, channel_id
):
    for illegal_char in illegal_char_list:
        word = word.replace(illegal_char, "")
    if (
        word.lower() == keyword_job.lower()
        and submission.id not in sent_submission_id_list
    ):
        await send_discord_message(submission, keyword_job, channel_id)
        sent_submission_id_list.append(submission.id)
        submission_json = {
            "submission_permalink": submission.permalink,
            "submission_id": submission.id,
            "created_at": datetime.now(),
        }
        await conn[DATABASE_NAME]["submission"].insert_one(submission_json)


@tasks.loop(seconds=10.0)
async def search_subreddits():
    await client.wait_until_ready()
    connect_to_mongo()
    conn = get_database()
    for guild in client.guilds:
        db_channel = await conn[DATABASE_NAME]["channel"].find_one(
            {"guild_id": guild.id}
        )
        if db_channel is None or db_channel["channel_id"] is None:
            print("Pass, channel not set")
        else:
            channel_id = int(db_channel["channel_id"])
            subreddit_raw_list = conn[DATABASE_NAME]["subreddit"].find(
                {"guild_id": guild.id}
            )
            job_keyword_raw_list = conn[DATABASE_NAME]["job_keyword"].find(
                {"guild_id": guild.id}
            )
            job_keyword_list = []
            sent_submission_raw_list = conn[DATABASE_NAME]["submission"].find()
            sent_submission_id_list = []
            async for submission in sent_submission_raw_list:
                sent_submission_id_list.append(submission["submission_id"])
            async for job_keyword_obj in job_keyword_raw_list:
                job_keyword_list.append(job_keyword_obj)
            async for subreddit_obj in subreddit_raw_list:
                try:
                    subreddit = await reddit.subreddit(subreddit_obj["subreddit"])
                    async for submission in subreddit.new(limit=10):
                        for job_keyword_obj in job_keyword_list:
                            job_keyword = job_keyword_obj["job_keyword"]
                            if submission.link_flair_text:
                                if (
                                    "hiring" in submission.link_flair_text.lower()
                                    and submission.id not in sent_submission_id_list
                                ):
                                    for word in submission.permalink.replace(
                                        "/", "_"
                                    ).split("_"):
                                        await search_for_illegal_words_and_trigger_message_sending(
                                            word,
                                            job_keyword,
                                            submission,
                                            sent_submission_id_list,
                                            conn,
                                            channel_id,
                                        )
                                    for word in submission.selftext.split(" "):
                                        await search_for_illegal_words_and_trigger_message_sending(
                                            word,
                                            job_keyword,
                                            submission,
                                            sent_submission_id_list,
                                            conn,
                                            channel_id,
                                        )
                except asyncprawcore.exceptions.ServerError as e:
                    if not bot_commands.SNOOZE:
                        await mention_admin_in_case_of_exceptions(e)
                    await asyncio.sleep(10)
                except Exception as e:
                    if not bot_commands.SNOOZE:
                        await mention_admin_in_case_of_exceptions(e)
                    await asyncio.sleep(10)


@commands.command(name="_exit")
async def graceful_exit(ctx):
    if ctx.message.author.id == DEXTER_ID:
        close_mongo_connection()
        await client.close()
    else:
        await ctx.send(
            "```Why the fuck are you trying to kill me?\n"
            "Only Dexter#4335 is allowed to do this.\n"
            "If you have any problem please, contact him!```"
        )


client.add_command(bot_commands.ping)
client.add_command(bot_commands.snooze)
client.add_command(bot_commands.custom_help)
client.add_command(graceful_exit)
client.add_command(bot_commands.subreddit)
client.add_command(bot_commands.job_keyword)
client.add_command(bot_commands.channel)
search_subreddits.start()
client.run(DISCORD_TOKEN)
