import asyncio
import logging

import discord
from discord.ext import commands

from config.database import db_manager
from config.settings import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GoGigBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
        )

    async def setup_hook(self):
        """Setup hook called when bot starts"""
        # Initialize database
        await db_manager.initialize()
        logger.info("Database initialized")

        # Load cogs
        await self.load_cogs()

        logger.info("Bot setup completed")

    async def load_cogs(self):
        """Load all cogs"""
        cogs = ["cogs.job_commands", "cogs.admin_commands", "cogs.utility_commands"]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}")
        await ctx.send(f"An error occurred: {str(error)}")

    async def close(self):
        """Cleanup when bot shuts down"""
        await db_manager.close()
        await super().close()


async def main():
    bot = GoGigBot()
    try:
        await bot.start(settings.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
