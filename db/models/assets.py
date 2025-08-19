from sqlalchemy import Column, String, Integer, DateTime

from ..base import Base


class Assets(Base):
    __tablename__ = 'assets'

    hash = Column(String, primary_key=True, nullable=False)
    domain_hash = Column(String, nullable=False)
    num_parts = Column(Integer, nullable=False)
    created_time = Column(DateTime, nullable=False)
