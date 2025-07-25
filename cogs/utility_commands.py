import discord
from discord.ext import commands


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.command(name="info")
    async def info(self, ctx):
        """Show bot information"""
        embed = discord.Embed(
            title="GoGig Bot",
            description="A Discord bot that finds job postings from Reddit and posts them to your server",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Version", value="2.0", inline=True)
        embed.add_field(name="Author", value="Tech-Dex", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
