from sqlalchemy import Column, Float, Integer, ForeignKey
from .user import User


class Labeler(User):
    """
    Labeler role, extending the User.
    """
    __tablename__ = "labelers"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    labeling_score = Column(Float, nullable=True)
