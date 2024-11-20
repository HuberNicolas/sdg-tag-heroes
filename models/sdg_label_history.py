from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class SDGLabelHistory(Base):
    __tablename__ = "sdg_label_histories"
    sdg_label_history_id = Column(Integer, primary_key=True, autoincrement=True)

    #
    """
        1 SDG Label is attached to exactly 1 SDG Label History
        1 SDG Label History is attached to exactly 1 SDG Label History
    """
    sdg_label_id = Column(Integer, ForeignKey("sdg_labels.sdg_label_id"))
    sdg_label = relationship("SDGLabel", back_populates="sdg_label_history")

    active = Column(Boolean, default=True)

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
        return f"<SDGLabelHistory(sdg_label_history_id={self.sdg_label_history_id})>"
