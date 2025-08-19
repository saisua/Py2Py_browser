from sqlalchemy import Column, String, DateTime, ForeignKey

from ..base import Base


class GroupMembers(Base):
    __tablename__ = 'group_members'

    group_hash = Column(
        String,
        ForeignKey('groups.hash', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    member_hash = Column(
        String,
        ForeignKey('peers.address', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    checked_time = Column(DateTime, nullable=False)
