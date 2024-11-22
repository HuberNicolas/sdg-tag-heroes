from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from models.base import Base


class SDGTarget(Base):
    __tablename__ = "sdg_targets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    index: Mapped[str] = mapped_column(String(10), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)
    target_vector_index: Mapped[int] = mapped_column(nullable=False)  # Updated field name for clarity
    icon: Mapped[str | None] = mapped_column(LONGTEXT)  # Base64 encoded SVG as LONGTEXT

    # Foreign key relationship to SDGGoal
    sdg_goal_id: Mapped[int] = mapped_column(ForeignKey("sdg_goals.id"), nullable=False)

    # Relationship with SDGGoal
    sdg_goal: Mapped["SDGGoal"] = relationship("SDGGoal", back_populates="sdg_targets")

    def __repr__(self):
        return f"<SDGTarget(index={self.index}, text={self.text}, SDGGoal={self.sdg_goal_id})>"
