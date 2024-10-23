from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from models.base import Base


class SDGGoal(Base):
    __tablename__ = "sdg_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index = Column(Integer, nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    color = Column(String(7), nullable=False)  # Hex code color
    icon = Column(LONGTEXT)  # Store the base64 encoded SVG as a BLOB

    # Define relationship with Target model
    sdg_targets = relationship("SDGTarget", back_populates="sdg_goal")

    def __repr__(self):
        return f"<SDGGoal(index={self.index}, name={self.name}, color={self.color})>"
