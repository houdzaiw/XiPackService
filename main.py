from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, License

Base.metadata.create_all(bind=engine)

app = FastAPI()


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
