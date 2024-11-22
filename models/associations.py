from sqlalchemy import Table, Column, ForeignKey
from models.base import Base

# Association table for many-to-many relationship between SDGLabelDecision and SDGUserLabel
sdg_label_decision_user_label_association = Table(
    "sdg_label_decision_user_label",
    Base.metadata,
    Column("decision_id", ForeignKey("sdg_label_decisions.decision_id"), primary_key=True),
    Column("user_label_id", ForeignKey("sdg_user_labels.label_id"), primary_key=True),
)
