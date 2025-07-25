import discord
from discord.ext import commands
from sqlalchemy import delete, func, select

from config.database import db_manager
from models.job import Job
from models.keyword import Keyword
from models.subreddit import Subreddit
from services.settings_service import get_setting, set_setting


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    @commands.has_permissions(administrator=True)
    async def stats(self, ctx):
        """Show bot statistics"""
        async with db_manager.get_session() as session:
            embed = discord.Embed(title="Bot Statistics", color=discord.Color.gold())
            embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
            embed.add_field(name="Users", value=len(self.bot.users), inline=True)
            embed.add_field(
                name="Active Jobs",
                value=(await session.execute(
                    select(func.count(Job.id)).where(Job.is_posted is True)
                )).scalar(),
                inline=True,
            )
            embed.add_field(
                name="Subreddits",
                value=(await session.execute(select(func.count(Subreddit.id)))).scalar(),
                inline=True,
            )
            embed.add_field(
                name="Keywords",
                value=(await session.execute(select(func.count(Keyword.id)))).scalar(),
                inline=True,
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=(
                    ctx.author.avatar.url
                    if ctx.author.avatar
                    else ctx.author.default_avatar.url
                ),
            )

            await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx, cog_name: str):
        """Reload a cog"""
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.send(f"✅ Reloaded cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload cog: {e}")

    @commands.command(name="add_subreddits")
    @commands.has_permissions(administrator=True)
    async def add_subreddits(self, ctx, *, names: str):
        """Add one or more subreddits (comma or space separated)"""
        items = [n.strip() for n in names.replace(",", " ").split() if n.strip()]
        async with db_manager.get_session() as session:
            added = []
            for name in items:
                exists = await session.execute(
                    select(Subreddit).where(Subreddit.name == name)
                )
                if not exists.scalar():
                    session.add(Subreddit(name=name))
                    added.append(name)
            await session.commit()
        await ctx.send(f"Added subreddits: {', '.join(added) if added else 'None'}")

    @commands.command(name="list_subreddits")
    @commands.has_permissions(administrator=True)
    async def list_subreddits(self, ctx):
        """List all subreddits"""
        async with db_manager.get_session() as session:
            result = await session.execute(select(Subreddit))
            names = [s.name for s in result.scalars()]
        await ctx.send(f"Subreddits: {', '.join(names) if names else 'None'}")

    @commands.command(name="remove_subreddits")
    @commands.has_permissions(administrator=True)
    async def remove_subreddits(self, ctx, *, names: str):
        """Remove one or more subreddits (comma or space separated)"""
        items = [n.strip() for n in names.replace(",", " ").split() if n.strip()]
        async with db_manager.get_session() as session:
            await session.execute(delete(Subreddit).where(Subreddit.name.in_(items)))
            await session.commit()
        await ctx.send(f"Removed subreddits: {', '.join(items)}")

    @commands.command(name="add_keywords")
    @commands.has_permissions(administrator=True)
    async def add_keywords(self, ctx, *, words: str):
        """Add one or more keywords (comma or space separated)"""
        items = [w.strip() for w in words.replace(",", " ").split() if w.strip()]
        async with db_manager.get_session() as session:
            added = []
            for word in items:
                exists = await session.execute(
                    select(Keyword).where(Keyword.word == word)
                )
                if not exists.scalar():
                    session.add(Keyword(word=word))
                    added.append(word)
            await session.commit()
        await ctx.send(f"Added keywords: {', '.join(added) if added else 'None'}")

    @commands.command(name="list_keywords")
    @commands.has_permissions(administrator=True)
    async def list_keywords(self, ctx):
        """List all keywords"""
        async with db_manager.get_session() as session:
            result = await session.execute(select(Keyword))
            words = [k.word for k in result.scalars()]
        await ctx.send(f"Keywords: {', '.join(words) if words else 'None'}")

    @commands.command(name="remove_keywords")
    @commands.has_permissions(administrator=True)
    async def remove_keywords(self, ctx, *, words: str):
        """Remove one or more keywords (comma or space separated)"""
        items = [w.strip() for w in words.replace(",", " ").split() if w.strip()]
        async with db_manager.get_session() as session:
            await session.execute(delete(Keyword).where(Keyword.word.in_(items)))
            await session.commit()
        await ctx.send(f"Removed keywords: {', '.join(items)}")

    @commands.command(name="set_channel")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel_type: str, channel: discord.TextChannel):
        """Set the Discord channel for jobs or logs. Usage: !set_channel jobs #channel or !set_channel logs #channel"""
        channel_type = channel_type.lower()
        if channel_type not in ["jobs", "logs"]:
            await ctx.send("Channel type must be 'jobs' or 'logs'.")
            return
        key = "DISCORD_CHANNEL_ID" if channel_type == "jobs" else "DISCORD_LOGS_CHANNEL_ID"
        async with db_manager.get_session() as session:
            await set_setting(session, key, str(channel.id))
        await ctx.send(f"{channel_type.capitalize()} channel set to {channel.mention} (ID: {channel.id}).")

    @commands.command(name="show_channels")
    @commands.has_permissions(administrator=True)
    async def show_channels(self, ctx):
        """Show current Discord and logs channel IDs from the database."""
        async with db_manager.get_session() as session:
            discord_channel = await get_setting(session, "DISCORD_CHANNEL_ID")
            logs_channel = await get_setting(session, "DISCORD_LOGS_CHANNEL_ID")
        await ctx.send(f"Discord channel ID: {discord_channel}\nLogs channel ID: {logs_channel}")


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
