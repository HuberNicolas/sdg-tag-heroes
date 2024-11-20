from sqlalchemy import Column, Float, ForeignKey, Integer
from .labeler import Labeler


class Expert(Labeler):
    """
    Expert role, extending the Labeler.
    """
    __tablename__ = "experts"

    id = Column(Integer, ForeignKey("labelers.id"), primary_key=True)
    expert_score = Column(Float, nullable=True)
