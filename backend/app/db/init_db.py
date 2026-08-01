import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine
from app.db.models import Base

logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
