from sqlalchemy import Column, String, Integer, ForeignKey, DateTime

from .base import Base


class StoredAssetHashes(Base):
    __tablename__ = 'stored_asset_hashes'

    hash = Column(
        String,
        ForeignKey('assets.hash', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    id = Column(Integer, primary_key=True, nullable=False)
    part = Column(Integer, primary_key=True, nullable=False)
    stored_dt = Column(DateTime, nullable=False)
