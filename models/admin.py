from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .user import User


class Admin(User):
    """
    Admin role, extending the User.
    """
    __tablename__ = "admins"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # Add relationships or admin-specific fields if needed
