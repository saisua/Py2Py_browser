import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import text

from config import db_protocol, db_dir

from .base import Base
from .peers import Peers
from .assets import Assets
from .asset_hints import AssetHints
from .stored_asset_parts import StoredAssetParts
from .stored_asset_hashes import StoredAssetHashes
from .groups import Groups
from .group_members import GroupMembers


async def setup_database():
    db_pardir = os.path.dirname(db_dir)
    if db_pardir:
        os.makedirs(db_pardir, exist_ok=True)

    engine = create_async_engine(f'{db_protocol}:///{db_dir}')

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    session_maker = async_sessionmaker(bind=engine)

    async with session_maker() as session:
        tables = await session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))
        table_names = {row[0] for row in tables}
        assert all(table in table_names for table in [
            'peers',
            'assets',
            'asset_hints',
            'stored_asset_part',
            'stored_asset_hashes',
            'groups',
            'group_members'
        ]), "Not all tables exist in the database"

    return engine, session_maker


engine, session_maker = asyncio.run(setup_database())

__all__ = [
    "Peers",
    "Assets",
    "AssetHints",
    "StoredAssetParts",
    "StoredAssetHashes",
    "Groups",
    "GroupMembers",
    "session_maker",
    "engine",
]
