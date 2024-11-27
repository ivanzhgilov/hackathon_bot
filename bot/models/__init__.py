from sqlalchemy.orm import relationship

from models.admin_password import AdminPassword
from models.core import Base
from models.request import Request
from models.user import User

User.requests = relationship("Request", order_by=Request.id, back_populates="user")
