from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import relationship

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base

class SDGLabel(Base):
    __tablename__ = "sdg_labels"
    publication_id = Column(
        Integer, ForeignKey("publications.publication_id"), primary_key=True
    )
    publication = relationship("Publication", back_populates="sdg_labels")

    # One-to-one relationship with SDGLabelHistory
    sdg_label_history = relationship("SDGLabelHistory", uselist=False, back_populates="sdg_label")

    # Columns for each SDG goal label
    sdg1 = Column(Integer, CheckConstraint('sdg1 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg2 = Column(Integer, CheckConstraint('sdg2 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg3 = Column(Integer, CheckConstraint('sdg3 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg4 = Column(Integer, CheckConstraint('sdg4 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg5 = Column(Integer, CheckConstraint('sdg5 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg6 = Column(Integer, CheckConstraint('sdg6 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg7 = Column(Integer, CheckConstraint('sdg7 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg8 = Column(Integer, CheckConstraint('sdg8 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg9 = Column(Integer, CheckConstraint('sdg9 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg10 = Column(Integer, CheckConstraint('sdg10 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg11 = Column(Integer, CheckConstraint('sdg11 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg12 = Column(Integer, CheckConstraint('sdg12 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg13 = Column(Integer, CheckConstraint('sdg13 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg14 = Column(Integer, CheckConstraint('sdg14 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg15 = Column(Integer, CheckConstraint('sdg15 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg16 = Column(Integer, CheckConstraint('sdg16 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg17 = Column(Integer, CheckConstraint('sdg17 IN (-1, 0, 1)'), nullable=False, default=0)



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
            f"<SDGLabel(publication_id={self.publication_id}, "
            f"sdg1={self.sdg1}, sdg2={self.sdg2}, sdg3={self.sdg3}, sdg4={self.sdg4}, "
            f"sdg5={self.sdg5}, sdg6={self.sdg6}, sdg7={self.sdg7}, sdg8={self.sdg8}, "
            f"sdg9={self.sdg9}, sdg10={self.sdg10}, sdg11={self.sdg11}, sdg12={self.sdg12}, "
            f"sdg13={self.sdg13}, sdg14={self.sdg14}, sdg15={self.sdg15}, sdg16={self.sdg16}, "
            f"sdg17={self.sdg17}>"
        )
