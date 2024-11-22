from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class SDGLabelDecision(Base):
    __tablename__ = "sdg_label_decisions"

    sdg_label_decision_id = Column(Integer, primary_key=True, autoincrement=True)


    #
    """
        1 SDG Label History contains N SDG Label Decisions
        N SDG Label Decisions belongs to exactly 1 SDG Label History
        
        Parent: SDG Label
        Child: SDG Label History
    """
    sdg_label_history_id = Column(Integer, ForeignKey("sdg_label_histories.sdg_label_history_id"))
    sdg_label_history = relationship("SDGLabelHistory", back_populates="sdg_label_decisions")


    #
    """
        N SDG User Label belongs to exactly 1 SDG Label Decision
        1 SDG Label Decision can contain N SDG User Labels
        
        Parent: SDG Label Decision
        Child: SDG User Label
    """
    sdg_user_label = relationship("SDGUserLabel",back_populates="sdg_label_decision",)

    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'), nullable=False)
    decision_value = Column(
        Integer, CheckConstraint('decision_value IN (-1, 0, 1)'), nullable=False, default=0
    )
    labeled_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )

    #
    """
        1 Expert can validate M SDG Label Decisions
        1 SDG Label Decision is validated by exactly 1 Expert
    """
    #expert_id = Column(Integer, ForeignKey("experts.user_id"), nullable=True)  # Reference to the expert's user_id
    #expert = relationship("Expert", back_populates="sdg_label_decisions")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        onupdate=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<SDGLabelDecision(decision_id={self.sdg_label_decision_id} "
            f"sdg={self.sdg}, decision_value={self.decision_value}, expert={self.expert})>"
        )
