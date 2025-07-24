import logging
from typing import Sequence, Any, Coroutine

from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from models.job import Job

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job: Job) -> Job:
        """Create a new job entry"""
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_job_by_reddit_id(self, reddit_id: str) -> Job | None:
        """Get job by Reddit ID"""
        result = await self.session.execute(
            select(Job).where(Job.reddit_id == reddit_id)
        )
        return result.scalar_one_or_none()

    async def get_unposted_jobs(self, limit: int = 10) -> Sequence[Job]:
        """Get unposted jobs"""
        result = await self.session.execute(
            select(Job)
            .where(Job.is_posted is False)
            .order_by(Job.created_utc.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_as_posted(self, job_id: int) -> bool:
        """Mark job as posted"""
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()

        if job:
            job.is_posted = True
            await self.session.commit()
            return True
        return False

    async def get_recent_jobs(self, limit: int = 20) -> Sequence[Job]:
        """Get recent jobs"""
        result = await self.session.execute(
            select(Job).order_by(Job.created_utc.desc()).limit(limit)
        )
        return result.scalars().all()
