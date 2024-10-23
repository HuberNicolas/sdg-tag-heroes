from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from models.base import Base


class SDGTarget(Base):
    __tablename__ = "sdg_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index = Column(String(10), nullable=False)
    text = Column(String(255), nullable=False)
    color = Column(String(7), nullable=False)
    targetVectorIndex = Column(Integer, nullable=False)
    icon = Column(LONGTEXT)  # Store the base64 encoded SVG as a LONGTEXT

    # Foreign key relationship to Goal table
    sdg_goal_id = Column(Integer, ForeignKey('sdg_goals.id'), nullable=False)

    # Relationship with Goal model
    sdg_goal = relationship("SDGGoal", back_populates="sdg_targets")

    def __repr__(self):
        return f"<SDGTarget(index={self.index}, text={self.text}, SDGGoal={self.sdg_goal_id})>"
