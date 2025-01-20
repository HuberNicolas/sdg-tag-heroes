from sqlalchemy import Table, Column, ForeignKey
from models.base import Base

# Association table for many-to-many relationship between SDGLabelDecision and SDGUserLabel
sdg_label_decision_user_label_association = Table(
    "sdg_label_decision_user_label",
    Base.metadata,
    Column("decision_id", ForeignKey("sdg_label_decisions.decision_id"), primary_key=True),
    Column("user_label_id", ForeignKey("sdg_user_labels.label_id"), primary_key=True),
)

# Association table for the many-to-many relationship between User and Group
user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.user_id"), primary_key=True),
    Column("group_id", ForeignKey("groups.group_id"), primary_key=True)
)

# Association table for the many-to-many relationship
publication_authors_association = Table(
    "publication_authors",
    Base.metadata,
    Column("publication_id", ForeignKey("publications.publication_id"), primary_key=True),
    Column("author_id", ForeignKey("authors.author_id"), primary_key=True),
)
