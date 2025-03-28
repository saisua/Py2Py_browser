from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint

from .base import Base


class Groups(Base):
    __tablename__ = 'groups'

    hash = Column(String, primary_key=True, nullable=False)
    checked_time = Column(DateTime, nullable=False)
    type = Column(
        Integer,
        CheckConstraint('type BETWEEN 0 AND 5'),
        nullable=False,
    )  # Type restricted to 0..5
    # identity_key = Column(String, nullable=False)
    # registration_id = Column(Integer, nullable=False)
    # pre_key_id = Column(Integer, nullable=False)
    # pre_key = Column(String, nullable=False)
    # pre_key_pub = Column(String, nullable=False)
    # signed_pre_key_id = Column(Integer, nullable=False)
    # signed_pre_key = Column(String, nullable=False)
    # signed_pre_key_pub = Column(String, nullable=False)
    # timestamp = Column(Integer, nullable=False)
