import logging
from datetime import datetime
from typing import AsyncGenerator

import asyncpraw

from config.settings import settings
from models.job import Job

logger = logging.getLogger(__name__)


class RedditService:
    def __init__(self):
        self.reddit = None

    async def initialize(self):
        """Initialize Reddit client"""
        self.reddit = asyncpraw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
        )

    async def search_jobs(
        self, subreddits: list[str], keywords: list[str], limit: int = 10
    ) -> AsyncGenerator[Job, None]:
        """Search for jobs in specified subreddits with keywords"""
        if not self.reddit:
            await self.initialize()

        for subreddit_name in subreddits:
            try:
                subreddit = await self.reddit.subreddit(subreddit_name)

                async for submission in subreddit.new(limit=limit):
                    if self._matches_keywords(submission.title, keywords):
                        job = Job(
                            reddit_id=submission.id,
                            title=submission.title,
                            content=submission.selftext,
                            author=str(submission.author),
                            subreddit=subreddit_name,
                            url=f"https://reddit.com{submission.permalink}",
                            created_utc=datetime.fromtimestamp(submission.created_utc),
                        )
                        yield job

            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {e}")

    @staticmethod
    def _matches_keywords(text: str, keywords: list[str]) -> bool:
        """Check if text contains any of the keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    async def close(self):
        """Close Reddit client"""
        if self.reddit:
            await self.reddit.close()
