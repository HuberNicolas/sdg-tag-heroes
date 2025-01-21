from datetime import datetime
from sqlalchemy import Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class ClusterTopic(Base):
    __tablename__ = 'cluster_topics'

    topic_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level_id: Mapped[int] = mapped_column(ForeignKey('cluster_levels.id'), nullable=False)
    cluster_id_str: Mapped[str] = mapped_column(String(255), nullable=False)  # Unique identifier, e.g., 'cluster1_level1_topic1'
    size: Mapped[float] = mapped_column(Float, nullable=False)
    center_x: Mapped[float] = mapped_column(Float, nullable=False)  # X-coordinate for the cluster center
    center_y: Mapped[float] = mapped_column(Float, nullable=False)  # Y-coordinate for the cluster center
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., 'topic1'
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Descriptive topic name

    # Relationship to ClusterLevel
    cluster_level: Mapped["ClusterLevel"] = relationship('ClusterLevel', back_populates='cluster_topics')

    # Relationship to PublicationCluster
    publications: Mapped[list["PublicationCluster"]] = relationship(
        "PublicationCluster", back_populates="cluster_topic", cascade="all, delete-orphan"
    )


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
