from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class SDGLabelHistory(Base):
    __tablename__ = "sdg_label_histories"
    publication_id = Column(
        Integer, ForeignKey("sdg_labels.publication_id"), primary_key=True
    )
    sdg_label = relationship("SDGLabel", back_populates="sdg_label_history")
    sdg_label_decisions = relationship("SDGLabelDecision", back_populates="sdg_label_history")

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
        return f"<SDGLabelHistory(publication_id={self.publication_id})>"
