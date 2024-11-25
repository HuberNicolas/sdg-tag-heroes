from sqlalchemy import Table, ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from models.base import Base

from models.associations import user_group_association

class Group(Base):
    """
    Group model for associating users.
    """
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Many-to-Many relationship with User
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_group_association,
        back_populates="groups"
    )
