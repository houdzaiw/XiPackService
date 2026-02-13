from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from database import Base
from datetime import datetime

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, unique=True, index=True)
    email = Column(String)
    device_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    order_id = Column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String, unique=True, index=True)
    email = Column(String)
    device_id = Column(String)
    amount = Column(Float)
    payment_method = Column(String)  # alipay or wechat
    status = Column(String, default="pending")  # pending, paid, expired, cancelled
    trade_no = Column(String, nullable=True)  # 支付平台交易号
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
