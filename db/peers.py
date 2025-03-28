from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    CheckConstraint,
    BINARY,
    LargeBinary,
    BigInteger,
)

from config.p2p_config import PeerType

from .base import Base


class Peers(Base):
    __tablename__ = 'peers'

    address = Column(BINARY, primary_key=True, nullable=False)
    checked_time = Column(DateTime, nullable=False)
    type = Column(
        Integer,
        CheckConstraint(f"type IN ({', '.join(map(str, PeerType))})"),
        nullable=False,
    )
    identity_key = Column(LargeBinary, nullable=False)
    registration_id = Column(Integer, nullable=False)
    pre_key_id = Column(Integer, nullable=False)
    pre_key = Column(LargeBinary, nullable=False)
    pre_key_pub = Column(LargeBinary, nullable=False)
    signed_pre_key_id = Column(Integer, nullable=False)
    signed_pre_key = Column(LargeBinary, nullable=False)
    signed_pre_key_pub = Column(LargeBinary, nullable=False)
    timestamp = Column(Integer, nullable=False)
    sid = Column(BigInteger, nullable=False)
