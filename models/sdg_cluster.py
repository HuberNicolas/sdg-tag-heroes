from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

# Cluster Group Table
class ClusterGroup(Base):
    __tablename__ = 'cluster_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Name of the SDG cluster group, e.g., 'cluster_group_01'

    # Relationship to cluster levels
    cluster_levels = relationship('ClusterLevel', back_populates='cluster_group')


# Cluster Level Table
class ClusterLevel(Base):
    __tablename__ = 'cluster_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_group_id = Column(Integer, ForeignKey('cluster_groups.id'), nullable=False)
    level_number = Column(Integer, nullable=False)  # Level number, e.g., 1 to 25

    # Relationship to ClusterGroup
    cluster_group = relationship('ClusterGroup', back_populates='cluster_levels')

    # Relationship to clusters
    cluster_topics = relationship('ClusterTopic', back_populates='cluster_level')


# Cluster Topic Table
class ClusterTopic(Base):
    __tablename__ = 'cluster_topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level_id = Column(Integer, ForeignKey('cluster_levels.id'), nullable=False)
    cluster_id = Column(String(255), nullable=False)  # Unique identifier, e.g., 'cluster1_level1_topic1'
    size = Column(Float, nullable=False)
    center_x = Column(Float, nullable=False)  # X-coordinate for the cluster center
    center_y = Column(Float, nullable=False)  # Y-coordinate for the cluster center
    name = Column(String(255), nullable=False)  # e.g., 'topic1'
    topic_name = Column(String(255), nullable=False)  # Descriptive topic name

    # Relationship to ClusterLevel
    cluster_level = relationship('ClusterLevel', back_populates='cluster_topics')
