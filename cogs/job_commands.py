import logging

import discord
from discord.ext import commands, tasks
from sqlalchemy import select

from config.database import db_manager
from config.settings import settings
from models.keyword import Keyword
from models.subreddit import Subreddit
from services.job_service import JobService
from services.reddit_service import RedditService

logger = logging.getLogger(__name__)


class JobCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit_service = RedditService()
        self.job_check_loop.start()

    async def cog_load(self):
        """Initialize services when cog loads"""
        await self.reddit_service.initialize()

    async def cog_unload(self):
        """Cleanup when cog unloads"""
        self.job_check_loop.cancel()
        await self.reddit_service.close()

    @tasks.loop(seconds=settings.CHECK_INTERVAL)
    async def job_check_loop(self):
        """Periodic job check and posting"""
        try:
            await self._check_and_post_jobs()
        except Exception as e:
            logger.error(f"Error in job check loop: {e}")
            await self._log_error_to_channel(f"Error in job check loop: {e}")

    @job_check_loop.before_loop
    async def before_job_check_loop(self):
        """Wait for bot to be ready before starting loop"""
        await self.bot.wait_until_ready()

    async def _check_and_post_jobs(self):
        """Check for new jobs and post them"""
        async with db_manager.get_session() as session:
            job_service = JobService(session)

            # Fetch subreddits and keywords from database
            subreddits_result = await session.execute(select(Subreddit))
            subreddits = [s.name for s in subreddits_result.scalars()]
            keywords_result = await session.execute(select(Keyword))
            keywords = [k.word for k in keywords_result.scalars()]

            # Search for new jobs
            async for job in self.reddit_service.search_jobs(
                subreddits, keywords, settings.MAX_JOBS_PER_CHECK
            ):
                # Check if job already exists
                existing_job = await job_service.get_job_by_reddit_id(job.reddit_id)
                if not existing_job:
                    # Save new job
                    await job_service.create_job(job)

                    # Post to Discord
                    await self._post_job_to_discord(job)
                    await job_service.mark_as_posted(job.id)

    async def _log_error_to_channel(self, error_message):
        """Send error message to the logs channel."""
        channel = self.bot.get_channel(settings.DISCORD_LOGS_CHANNEL_ID)
        if channel:
            await channel.send(f":warning: {error_message}")

    async def _post_job_to_discord(self, job):
        """Post job to Discord channel"""
        channel = self.bot.get_channel(settings.DISCORD_CHANNEL_ID)
        if not channel:
            logger.error(f"Channel {settings.DISCORD_CHANNEL_ID} not found")
            await self._log_error_to_channel(f"Channel {settings.DISCORD_CHANNEL_ID} not found")
            return

        embed = discord.Embed(
            title=job.title[:250] + "..." if len(job.title) > 250 else job.title,
            url=job.url,
            description=(
                job.content[:500] + "..." if len(job.content) > 500 else job.content
            ),
            color=discord.Color.green(),
        )
        embed.add_field(name="Subreddit", value=f"r/{job.subreddit}", inline=True)
        embed.add_field(name="Author", value=f"u/{job.author}", inline=True)
        embed.set_footer(
            text=f"Posted: {job.created_utc.strftime('%Y-%m-%d %H:%M UTC')}"
        )

        await channel.send(embed=embed)

    @commands.command(name="jobs")
    async def list_recent_jobs(self, ctx, limit: int = 5):
        """List recent jobs"""
        if limit > 20:
            limit = 20

        async with db_manager.get_session() as session:
            job_service = JobService(session)
            jobs = await job_service.get_recent_jobs(limit)

            if not jobs:
                await ctx.send("No jobs found.")
                return

            embed = discord.Embed(
                title=f"Recent {len(jobs)} Jobs", color=discord.Color.blue()
            )

            for job in jobs:
                embed.add_field(
                    name=job.title[:50] + "..." if len(job.title) > 50 else job.title,
                    value=f"r/{job.subreddit} • [Link]({job.url})",
                    inline=False,
                )

            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(JobCommands(bot))
