#! usr/bin/env python3
import asyncpraw
import pprint
import time
import asyncprawcore
import asyncio
import discord
import os
import sys
from discord.ext import tasks

pp = pprint.PrettyPrinter(indent=4)

name_subreddit_list = ['forhire', 'jobbit', 'freelance_forhire', 'RemoteJobs']
sent_submission_id_list = list()
keyword_job_list = ['developer', 'junior', 'mid', 'intermediate', 'senior', 'software',
                    'backend', 'frontend', 'fullstack', 'web', 'full-stack',
                    'java', 'python', 'javascript', 'typescript', 'node', 'nodejs', 'deno', 'denojs',
                    'angular', 'react', 'vue', 'django', 'flask', 'fastapi', 'spring', 'boot']
illegal_char_list = ['.', ',', '!', '?']

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
ADMIN_ROLE_ID = os.getenv('ADMIN_ROLE_ID')
CHANNEL_TO_POST_ID = os.getenv('CHANNEL_TO_POST_ID')
CHANNEL_LOGS_ID = os.getenv('CHANNEL_LOGS_ID')
GUILD_ID: int = -1

reddit = asyncpraw.Reddit(client_id=f'{os.getenv("CLIENT_ID")}',
                          client_secret=f'{os.getenv("CLIENT_SECRET")}',
                          user_agent='Reddit Job Finder Discord Bot',
                          username=f'{os.getenv("REDDIT_USER")}',
                          password=f'{os.getenv("REDDIT_PASSWORD")}')
client = discord.Client()


@client.event
async def on_ready():
    global GUILD_ID
    for guild in client.guilds:
        if guild.name == DISCORD_GUILD:
            GUILD_ID = guild.id
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
        else:
            sys.exit("The bot is not linked to the Guild you declared")


def build_discord_embed_message(submission, keyword):
    description = submission.selftext
    if len(description) > 2048:
        description = submission.selftext[:2044] + '...'
    embed = discord.Embed(title=f'{submission.title}',
                          color=discord.Colour(0x82de09),
                          url=f'https://www.reddit.com{submission.permalink}',
                          description=f'{description}',
                          )
    embed.set_image(url=f'')
    embed.set_thumbnail(url=f'')
    embed.set_author(name=f'{submission.author.name}')
    embed.set_footer(text=f'Subreddit {submission.subreddit_name_prefixed} '
                          f'| {time.strftime("%a %b %d, %Y at %H:%M:%S", time.gmtime(submission.created_utc))}')
    try:
        embed.set_thumbnail(url=f'{submission.preview["images"][0]["source"]["url"]}')
    except AttributeError:
        pass
    embed.add_field(name=f'#️⃣', value=f'{keyword.capitalize()}', inline=False)
    embed.add_field(name=f'👍', value=f'{submission.ups}', inline=True)
    embed.add_field(name=f'👎', value=f'{submission.downs}', inline=True)
    embed.add_field(name=f'💬', value=f'{submission.num_comments}', inline=True)

    return embed


def build_discord_embed_logs(e):
    embed = discord.Embed(title=f' {e.__name__}',
                          color=discord.Colour(0xe74c3c),
                          description=f'{e.__doc__}',
                          )

    return embed


async def send_discord_message(submission, keyword):
    channel = client.get_channel(int(CHANNEL_TO_POST_ID))

    await channel.send(embed=build_discord_embed_message(submission, keyword))
    # print(f'Link : https://www.reddit.com{submission.permalink}')


async def mention_admin_in_case_of_exceptions(e):
    global GUILD_ID
    channel = client.get_channel(int(CHANNEL_LOGS_ID))
    if GUILD_ID != -1:
        guild = client.get_guild(id=GUILD_ID)
        admin = discord.utils.get(guild.roles, id=int(ADMIN_ROLE_ID))
        await channel.send(f'{admin.mention} I\'m sick, please help me!', embed=build_discord_embed_logs(admin, e))


async def search_for_illegal_words_and_trigger_message_sending(word, keyword_job, submission):
    for illegal_char in illegal_char_list:
        word = word.replace(illegal_char, '')
    if word.lower() == keyword_job.lower() and submission.id not in sent_submission_id_list:
        await send_discord_message(submission, keyword_job)
        sent_submission_id_list.append(submission.id)


@tasks.loop(seconds=10.0)
async def search_subreddits():
    await client.wait_until_ready()
    for subreddit_name in name_subreddit_list:
        try:
            subreddit = await reddit.subreddit(subreddit_name)
            async for submission in subreddit.new(limit=10):
                for keyword_job in keyword_job_list:
                    if submission.link_flair_text == 'Hiring':
                        for word in submission.permalink:
                            await search_for_illegal_words_and_trigger_message_sending(word, keyword_job, submission)
                        for word in submission.selftext:
                            await search_for_illegal_words_and_trigger_message_sending(word, keyword_job, submission)
        except asyncprawcore.exceptions.ServerError as e:
            await mention_admin_in_case_of_exceptions(e)
            await asyncio.sleep(10)
        except Exception as e:
            await mention_admin_in_case_of_exceptions(e)
            await asyncio.sleep(10)


search_subreddits.start()
client.run(DISCORD_TOKEN)
