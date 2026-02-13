from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, unique=True, index=True)
    email = Column(String)
    device_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
