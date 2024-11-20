from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class Annotation(Base):
    __tablename__ = "annotations"

    annotation_id = Column(Integer, primary_key=True, autoincrement=True)

    #
    """
        1 User can write N annotations.
        1 Annotation is written by exactly 1 User
    """
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user = relationship("User", backref="annotations")

    #
    """
        1 SDGUserLabel can have N annotations from different or from the same user
        1 Annotation is attached to exactly 1 SDGUserLabel
    """
    sdg_user_label_id = Column(Integer, ForeignKey("sdg_user_labels.sdg_user_label_id"), nullable=False)
    sdg_user_label = relationship("SDGUserLabel", back_populates="annotations")


    #
    """
        1 Vote corresponds to 1 annotation, but 1 annotation can have N votes
        1 Annotation can have N votes either positive, negative or neutral
    """


    votes = relationship("Vote", back_populates="annotation", cascade="all, delete-orphan")

    content = Column(Text, nullable=False)  # Annotation content

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
            f"<Annotation(id={self.annotation_id}"
            f"user_id={self.user_id}, content={self.content[:30]}...)>"
        )
