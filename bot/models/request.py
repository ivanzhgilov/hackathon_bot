import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from models import Base


class RequestStatus(enum.Enum):
    SUCCESSFUL = 'successful'
    UNSUCCESSFUL = 'unsuccessful'
    ESCALATION = 'escalation'


class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(Enum(RequestStatus), nullable=True)

    user = relationship("User", back_populates="requests")

