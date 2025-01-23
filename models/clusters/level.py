from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class ClusterLevel(Base):
    __tablename__ = 'cluster_levels'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cluster_group_id: Mapped[int] = mapped_column(ForeignKey('cluster_groups.id'), nullable=False)
    level_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Level number, e.g., 1 to 25

    # Relationship to ClusterGroup
    cluster_group: Mapped["ClusterGroup"] = relationship('ClusterGroup', back_populates='cluster_levels')

    # Relationship to clusters
    cluster_topics: Mapped[list["ClusterTopic"]] = relationship('ClusterTopic', back_populates='cluster_level')


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        onupdate=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        nullable=False,
    )
