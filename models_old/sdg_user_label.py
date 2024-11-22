from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import relationship
from models.base import Base

from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()


class SDGUserLabel(Base):
    __tablename__ = "sdg_user_labels"
    sdg_user_label_id = Column(Integer, primary_key=True, autoincrement=True)


    #
    """
        1 SDG Label Decision can have N SDG User Labels
        1 SDG User Label is attached to exactly 1 SDG Label Decision
        
        Parent: SDG Label Decision
        Child: SDG User Label
    """
    sdg_label_decision_id = Column(Integer, ForeignKey("sdg_label_decisions.sdg_label_decision_id"))
    sdg_label_decision = relationship("SDGLabelDecision", back_populates="sdg_user_label")

    #
    """
        1 User can write N SDG User Labels
        N SDG User Label can be written by 1 User
        Parent: SDG User Label
        Child: User
    """
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # The user who made the annotation
    user = relationship("User", back_populates="sdg_user_labels")

    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'), nullable=False)
    comment = Column(Text, nullable=True)

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
            f"<SDGUserLabel(sdg_user_label_id={self.sdg_user_label_id},"
            f"user_id={self.user_id}, sdg={self.sdg})>"
        )
