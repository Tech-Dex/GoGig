import time

import discord
from discord.ext import commands

SNOOZE = False


@commands.command(name="_snooze")
async def snooze(ctx, *args):
    global SNOOZE
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
            await ctx.send("The command form is: ``` $sudo_snooze <on> or <off> ```")


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
        value="""Turn on/off option of sending logs about errors.\n
        Type $sudo_snooze command for more info.""",
        inline=False,
    )
    embed.add_field(name="_help", value="Shows this message", inline=False)

    return embed
