import time
from datetime import datetime

import discord
from discord.ext import commands

from core.config import ADMIN_ROLE_ID, DATABASE_NAME
from db.mongodb import get_database

SNOOZE = False


@commands.command(name="_snooze")
async def snooze(ctx, *args):
    global SNOOZE
    if discord.utils.get(ctx.message.author.roles, id=ADMIN_ROLE_ID):
        if len(args) > 1 or len(args) == 0:
            await ctx.send("The command form is: ``` $sudo_snooze <on> or <off> ```")
        elif len(args) == 1:
            if str(args[0]).lower() == "off":
                if SNOOZE is False:
                    await ctx.send("Snooze is already off!")
                else:
                    SNOOZE = False
                    await ctx.send("Snooze is off")
            elif str(args[0]).lower() == "on":
                if SNOOZE is True:
                    await ctx.send("Snooze is already on!")
                else:
                    SNOOZE = True
                    await ctx.send("Snooze is on!")
            else:
                await ctx.send(
                    "The command form is: ``` $sudo_snooze <on> or <off> ```"
                )
    else:
        await ctx.send(
            "The command is available only for administrators. Please contact one of them!"
        )


@commands.command(name="_help")
async def custom_help(ctx):
    await ctx.send(embed=embed_help())


def embed_help():
    embed = discord.Embed(
        title="Help Page",
        color=discord.Colour(0x2ECC71),
        url="https://ibb.co/gdqz4ZM",
        description="For a better version please check GitHub.",
    )
    embed.set_image(
        url="https://media.discordapp.net/attachments/811254175660638258/813764726160228352/logo.png"
    )
    embed.set_footer(
        text="GoGIG Bot "
        f'| {time.strftime("%a %b %d, %Y at %H:%M:%S", time.gmtime(time.time()))}'
    )
    embed.add_field(
        name="_snooze",
        value="""Turn on/off option of sending logs about errors.
        Type **$sudo_snooze** command for more info.""",
        inline=False,
    )
    embed.add_field(
        name="_subreddit",
        value="""Interact with GoGig database for you server. View and edit subreddits that you follow.
        Type **$sudo_subreddit** command for more info.""",
        inline=False,
    )
    embed.add_field(
        name="_job_keyword",
        value="""Interact with GoGig database for you server. View and edit job keywords that you are interested in.
        Type **$sudo_job_keyword** command for more info.""",
        inline=False,
    )
    embed.add_field(
        name="_channel",
        value="""Interact with GoGig database for you server. View, set and remove channel for submission
        Type **$sudo_channel** command for more info.""",
        inline=False,
    )
    embed.add_field(name="_help", value="Shows this message", inline=False)

    return embed


@commands.command(name="_ping")
async def ping(ctx):
    await ctx.send("Stop pinging me. I am alive!")


@commands.command(name="_subreddit")
async def subreddit(ctx, *args):
    conn = get_database()
    if len(args) == 0:
        await ctx.send(
            "The command form is: "
            "```"
            "$sudo_subreddit list\n"
            '$sudo_subreddit add ["subreddit name",]\n'
            '$sudo_subreddit remove ["subreddit name",.]\n'
            "```"
        )
    elif len(args) == 1:
        if str(args[0]).lower() == "list":
            subreddit_raw_list = conn[DATABASE_NAME]["subreddit"].find()
            message = (
                f"This is the list of subreddits followed in {ctx.author.guild}: ```["
            )
            async for subreddit_obj in subreddit_raw_list:
                message += f" {subreddit_obj['subreddit']},"
            message = message[:-1] + " ]```"
            await ctx.send(message)
    elif str(args[0]).lower() == "add":
        already_added_subreddits = []
        added_subreddits = []
        docs = []
        for arg in args[1:]:
            if await conn[DATABASE_NAME]["subreddit"].find_one({"subreddit": arg}):
                already_added_subreddits.append(arg)
                continue
            subreddit_json = {
                "subreddit": arg,
                "user": ctx.message.author.name,
                "user_id": ctx.message.author.id,
                "guild_id": ctx.message.guild.id,
                "created_at": datetime.now(),
            }
            added_subreddits.append(arg)
            docs.append(subreddit_json)
        if docs:
            await conn[DATABASE_NAME]["subreddit"].insert_many(docs)
            message_success = (
                f"Subreddits successfully added in {ctx.author.guild}:"
                "``` " + ", ".join(added_subreddits) + "```"
            )
            await ctx.send(message_success)
        else:
            await ctx.send("I was unable to add any subreddit.")
        if already_added_subreddits:
            message_failed = (
                f"Subreddits already added in {ctx.author.guild}:"
                "``` " + ", ".join(already_added_subreddits) + "```"
            )
            await ctx.send(message_failed)
    elif str(args[0]).lower() == "remove":
        response = await conn[DATABASE_NAME]["subreddit"].delete_many(
            {"guild_id": ctx.message.guild.id, "subreddit": {"$in": args[1:]}}
        )
        await ctx.send(f"Successfully deleted {response.deleted_count} subreddits.")


@commands.command(name="_job_keyword")
async def job_keyword(ctx, *args):
    conn = get_database()
    if len(args) == 0:
        await ctx.send(
            "The command form is: "
            "```"
            "$sudo_job_keyword list\n"
            '$sudo_job_keyword add ["job keyword",]\n'
            '$sudo_job_keyword remove ["job keyword",.]\n'
            "```"
        )
    elif len(args) == 1:
        if str(args[0]).lower() == "list":
            subreddit_raw_list = conn[DATABASE_NAME]["job_keyword"].find()
            message = (
                f"This is the list of job keywords used in {ctx.author.guild}: ```["
            )
            async for subreddit_obj in subreddit_raw_list:
                message += f" {subreddit_obj['job_keyword']},"
            message = message[:-1] + " ]```"
            await ctx.send(message)
    elif str(args[0]).lower() == "add":
        already_added_job_keywords = []
        added_job_keywords = []
        docs = []
        for arg in args[1:]:
            if await conn[DATABASE_NAME]["job_keyword"].find_one({"job_keyword": arg}):
                already_added_job_keywords.append(arg)
                continue
            subreddit_json = {
                "job_keyword": arg,
                "user": ctx.message.author.name,
                "user_id": ctx.message.author,
                "guild_id": ctx.message.guild.id,
                "created_at": datetime.now(),
            }
            added_job_keywords.append(arg)
            docs.append(subreddit_json)
        if docs:
            await conn[DATABASE_NAME]["job_keyword"].insert_many(docs)
            message_success = (
                f"Job keywords successfully added in {ctx.author.guild}:"
                "``` " + ", ".join(added_job_keywords) + "```"
            )
            await ctx.send(message_success)
        else:
            await ctx.send("I was unable to add any job keyword.")
        if already_added_job_keywords:
            message_failed = (
                f"Job keywords already added in {ctx.author.guild}:"
                "``` " + ", ".join(already_added_job_keywords) + "```"
            )
            await ctx.send(message_failed)
    elif str(args[0]).lower() == "remove":
        response = await conn[DATABASE_NAME]["job_keyword"].delete_many(
            {"guild_id": ctx.message.guild.id, "job_keyword": {"$in": args[1:]}}
        )
        await ctx.send(f"Successfully deleted {response.deleted_count} job keywords.")


@commands.command(name="_channel")
async def channel(ctx, *args):
    conn = get_database()
    if len(args) == 0:
        await ctx.send(
            "The command form is: "
            "```"
            "$sudo_channel view\n"
            "$sudo_channel set #channel\n"
            "$sudo_channel remove\n"
            "```"
        )
    elif len(args) == 1:
        if str(args[0]).lower() == "view":
            channel_obj = await conn[DATABASE_NAME]["channel"].find_one(
                {"guild_id": ctx.message.guild.id}
            )
            message = f"Submission are sent in channel: <#{channel_obj['channel_id']}>"
            await ctx.send(message)
        elif str(args[0]).lower() == "remove":
            channel_obj = await conn[DATABASE_NAME]["channel"].find_one(
                {"guild_id": ctx.message.guild.id}
            )
            if channel_obj:
                if channel_obj["channel_id"] is None:
                    message = "No previous value vor submission channel, can't remove something that was not set."
                    await ctx.send(message)
                else:
                    channel_json = {
                        "channel_id": None,
                        "user": ctx.message.author.name,
                        "user_id": ctx.message.author.id,
                        "guild_id": ctx.message.guild.id,
                        "created_at": datetime.now(),
                    }
                    await conn[DATABASE_NAME]["channel"].update_one(
                        {"guild_id": ctx.message.guild.id}, {"$set": channel_json}
                    )
                    message = "Submission channel removed. Submission will not be sent anymore."
                    await ctx.send(message)
            else:
                message = "No previous value vor submission channel, can't remove something that was not set."
                await ctx.send(message)

    elif str(args[0]).lower() == "set":
        channel_id = args[1][2:-1]
        channel_json = {
            "channel_id": channel_id,
            "user": ctx.message.author.name,
            "user_id": ctx.message.author.id,
            "guild_id": ctx.message.guild.id,
            "created_at": datetime.now(),
        }
        db_channel = await conn[DATABASE_NAME]["channel"].find_one(
            {"guild_id": ctx.message.guild.id}
        )
        if db_channel:
            await conn[DATABASE_NAME]["channel"].update_one(
                {"guild_id": ctx.message.guild.id}, {"$set": channel_json}
            )
        else:
            await conn[DATABASE_NAME]["channel"].insert_one(channel_json)
        message = f"Submission will be sent in channel: <#{channel_id}>"
        await ctx.send(message)
