from sqlalchemy import Column, String, Integer, ForeignKey

from ..base import Base


class AssetHints(Base):
    __tablename__ = 'asset_hints'

    hash = Column(
        String,
        ForeignKey('assets.hash', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    part = Column(Integer, primary_key=True, nullable=False)
    address_from = Column(
        String,
        ForeignKey('peers.address', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    num_parts = Column(Integer, nullable=True)
