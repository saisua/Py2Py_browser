import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from config import db_protocol, db_dir

from .base import Base
from .peers import Peers
from .assets import Assets
from .asset_hints import AssetHints
from .stored_asset_parts import StoredAssetParts
from .stored_asset_hashes import StoredAssetHashes


async def setup_database():
    db_pardir = os.path.dirname(db_dir)
    if db_pardir:
        os.makedirs(db_pardir, exist_ok=True)
    engine = create_async_engine(f'{db_protocol}:///{db_dir}')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(bind=engine)
    return engine, session_maker


engine, session_maker = asyncio.run(setup_database())


def __getattr__(name):
    match name:
        case "Peers":
            return Peers
        case "Assets":
            return Assets
        case "AssetHints":
            return AssetHints
        case "StoredAssetParts":
            return StoredAssetParts
        case "StoredAssetHashes":
            return StoredAssetHashes
        case "session_maker":
            return session_maker
        case "engine":
            return engine
        case _:
            raise AttributeError(f"Module 'db' has no attribute '{name}'")
