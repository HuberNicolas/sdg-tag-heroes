from datetime import datetime
from sqlalchemy import Integer, Float, String, ForeignKey, Table, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()


class PublicationCluster(Base):
    __tablename__ = "publication_clusters"
    publication_cluster_id = Column(Integer, autoincrement=True, primary_key=True)

    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"))
    cluster_id: Mapped[int] = mapped_column(ForeignKey("cluster_topics.topic_id"))
    cluster_id_string: Mapped[str] = mapped_column(String(255), nullable=False)
    sdg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    topic: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    publication: Mapped["Publication"] = relationship("Publication", back_populates="clusters")
    cluster_topic: Mapped["ClusterTopic"] = relationship("ClusterTopic", back_populates="publications")

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
