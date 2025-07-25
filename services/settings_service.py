from sqlalchemy.ext.asyncio import AsyncSession
from models.setting import Setting
from sqlalchemy import select

async def get_setting(session: AsyncSession, key: str) -> str | None:
    result = await session.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None

async def set_setting(session: AsyncSession, key: str, value: str):
    result = await session.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        session.add(setting)
    await session.commit()

