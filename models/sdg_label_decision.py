from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class SDGLabelDecision(Base):
    __tablename__ = "sdg_label_decisions"
    decision_id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(
        Integer, ForeignKey("sdg_label_histories.publication_id"), nullable=False
    )
    sdg_label_history = relationship("SDGLabelHistory", back_populates="sdg_label_decisions")

    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'), nullable=False)
    decision_value = Column(
        Integer, CheckConstraint('decision_value IN (-1, 0, 1)'), nullable=False, default=0
    )
    labeled_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )
    expert = Column(String(255), nullable=False)

    sdg_user_labels = relationship("SDGUserLabel", back_populates="sdg_label_decision")

    def __repr__(self):
        return (
            f"<SDGLabelDecision(decision_id={self.decision_id}, publication_id={self.publication_id}, "
            f"sdg={self.sdg}, decision_value={self.decision_value}, expert={self.expert})>"
        )
