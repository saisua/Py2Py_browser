import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import db_protocol, db_dir


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        f'{db_protocol}:///{db_dir}',
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session
    await engine.dispose()
