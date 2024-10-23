from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class SDGUserLabel(Base):
    __tablename__ = "sdg_user_labels"
    user_label_id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(Integer, ForeignKey("sdg_label_decisions.decision_id"), nullable=False)
    sdg_label_decision = relationship("SDGLabelDecision", back_populates="sdg_user_labels")

    user_id = Column(String(255), nullable=False)
    sdg = Column(Integer, CheckConstraint('sdg BETWEEN 1 AND 17'), nullable=False)
    publication_id = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<SDGUserLabel(user_label_id={self.user_label_id}, decision_id={self.decision_id}, "
            f"user_id={self.user_id}, sdg={self.sdg}, publication_id={self.publication_id})>"
        )
