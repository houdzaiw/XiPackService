from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, License, Order
from datetime import datetime
from pydantic import BaseModel, EmailStr
import uuid
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置
LICENSE_PRICE = 99.00  # 价格（元）
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-password")

# 请求模型
class OrderCreateRequest(BaseModel):
    email: EmailStr
    device_id: str
    payment_method: str  # alipay or wechat

class PaymentCallbackRequest(BaseModel):
    trade_no: str
    order_no: str
    total_amount: float
    trade_status: str

# 生成激活码
def generate_license_key() -> str:
    """生成32位激活码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(32))

# 生成订单号
def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(secrets.choice(string.digits) for _ in range(6))
    return f"XP{timestamp}{random_suffix}"

# 发送邮件
def send_license_email(email: str, license_key: str, order_no: str):
    """发送激活码邮件"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'XiPack 激活码 - 购买成功'
        msg['From'] = EMAIL_USER
        msg['To'] = email
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">感谢您购买 XiPack！</h2>
            <p>您的激活码已生成：</p>
            <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <p style="font-size: 24px; font-weight: bold; color: #007AFF; margin: 0;">
                    {license_key}
                </p>
            </div>
            <p><strong>订单号：</strong>{order_no}</p>
            <p>请在 XiPack 应用中输入此激活码以激活您的许可证。</p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                如有任何问题，请联系客服。<br>
                此邮件由系统自动发送，请勿直接回复。
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False


@app.post("/verify")
def verify_license(data: dict):
    license_key = data.get("license_key")
    device_id = data.get("device_id")

    db: Session = SessionLocal()

    license = db.query(License).filter(
        License.license_key == license_key
    ).first()

    if not license:
        raise HTTPException(status_code=400, detail="Invalid license")

    if not license.is_active:
        raise HTTPException(status_code=400, detail="License inactive")

    # 首次绑定设备
    if not license.device_id:
        license.device_id = device_id
        db.commit()

    # 已绑定但不是同一设备
    elif license.device_id != device_id:
        raise HTTPException(status_code=400, detail="Device mismatch")

    return {
        "status": "valid",
        "license_key": license_key
    }


@app.post("/api/order/create")
def create_order(request: OrderCreateRequest):
    """创建订单"""
    db: Session = SessionLocal()
    
    try:
        # 生成订单号
        order_no = generate_order_no()
        
        # 创建订单
        order = Order(
            order_no=order_no,
            email=request.email,
            device_id=request.device_id,
            amount=LICENSE_PRICE,
            payment_method=request.payment_method,
            status="pending"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 返回订单信息和支付二维码URL（实际应用中需要调用支付宝/微信API生成）
        payment_url = f"https://qr.alipay.com/fake_payment?order_no={order_no}&amount={LICENSE_PRICE}"
        
        return {
            "success": True,
            "order_no": order_no,
            "amount": LICENSE_PRICE,
            "payment_url": payment_url,
            "qr_code": payment_url  # 在实际应用中，这应该是生成的二维码图片
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/payment/callback")
async def payment_callback(request: Request):
    """支付回调处理（支付宝和微信通用）"""
    db: Session = SessionLocal()
    
    try:
        # 获取回调数据
        data = await request.json()
        order_no = data.get("order_no")
        trade_no = data.get("trade_no")
        trade_status = data.get("trade_status", "TRADE_SUCCESS")
        
        if not order_no:
            raise HTTPException(status_code=400, detail="Missing order_no")
        
        # 查找订单
        order = db.query(Order).filter(Order.order_no == order_no).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # 如果订单已处理，直接返回
        if order.status == "paid":
            return {"success": True, "message": "Already processed"}
        
        # 更新订单状态（实际应用中需要验证支付签名）
        if trade_status == "TRADE_SUCCESS":
            order.status = "paid"
            order.trade_no = trade_no
            order.paid_at = datetime.utcnow()
            
            # 生成激活码
            license_key = generate_license_key()
            
            # 创建许可证
            license = License(
                license_key=license_key,
                email=order.email,
                device_id=order.device_id,
                is_active=True,
                order_id=order.order_no
            )
            
            db.add(license)
            db.commit()
            
            # 发送邮件
            send_license_email(order.email, license_key, order.order_no)
            
            return {
                "success": True,
                "license_key": license_key,
                "message": "Payment successful"
            }
        
        return {"success": False, "message": "Payment failed"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/order/status/{order_no}")
def get_order_status(order_no: str):
    """查询订单状态"""
    db: Session = SessionLocal()
    
    try:
        order = db.query(Order).filter(Order.order_no == order_no).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        response = {
            "order_no": order.order_no,
            "status": order.status,
            "amount": order.amount,
            "created_at": order.created_at.isoformat(),
        }
        
        # 如果已支付，返回激活码
        if order.status == "paid":
            license = db.query(License).filter(
                License.order_id == order.order_no
            ).first()
            if license:
                response["license_key"] = license.license_key
        
        return response
        
    finally:
        db.close()


# 用于测试的模拟支付端点
@app.post("/api/payment/simulate")
def simulate_payment(order_no: str):
    """模拟支付成功（仅用于测试）"""
    db: Session = SessionLocal()
    
    try:
        order = db.query(Order).filter(Order.order_no == order_no).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status == "paid":
            return {"success": True, "message": "Already paid"}
        
        # 模拟支付成功
        order.status = "paid"
        order.trade_no = f"TEST_{uuid.uuid4().hex[:16]}"
        order.paid_at = datetime.utcnow()
        
        # 生成激活码
        license_key = generate_license_key()
        
        # 创建许可证
        license = License(
            license_key=license_key,
            email=order.email,
            device_id=order.device_id,
            is_active=True,
            order_id=order.order_no
        )
        
        db.add(license)
        db.commit()
        
        # 发送邮件
        send_license_email(order.email, license_key, order.order_no)
        
        return {
            "success": True,
            "license_key": license_key,
            "message": "Payment simulated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
