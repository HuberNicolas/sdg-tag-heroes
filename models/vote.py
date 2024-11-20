from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import Base
from enum import Enum as PyEnum


class VoteRole(PyEnum):
    POSITIVE = "up-vote"
    NEGATIVE = "down-vote"
    NEUTRAL = "neutral"

class Vote(Base):
    __tablename__ = 'user_votes'

    vote_id = Column(Integer, primary_key=True, index=True)

    #
    """
        1 User can have N Votes
        1 Vote is attached to exactly 1 User
    """
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    user = relationship("User", back_populates="votes")

    #
    """
        1 Annotation can have N Votes
        1 Vote is attached to exactly 1 Annotation
    """
    annotation_id = Column(Integer, ForeignKey('annotations.annotation_id'), nullable=False)
    annotation = relationship("Annotation", back_populates="votes")


    vote_type = Column(Enum(VoteRole), default=VoteRole.NEUTRAL,nullable=True)
    score = Column(Integer, nullable=False)


    def __repr__(self):
        return (
            f"<Vote(id={self.vote_id}, annotation_id={self.annotation_id}, user_id={self.user_id}, "
            f"vote_type={self.vote_type}, score={self.score})>"
        )
