# XiPackService 支付系统配置指南

## 功能概述

已为 XiPack 打包工具实现完整的激活码付费系统：

1. ✅ 付费网页（支付宝/微信扫码支付）
2. ✅ 订单管理和激活码生成
3. ✅ 邮件自动发送激活码
4. ✅ Swift 应用集成购买按钮

## 快速开始

### 1. 安装依赖

```bash
cd /Users/huili/project/XiPackService
pip install -r requirements.txt
```

### 2. 配置邮件服务

设置环境变量来配置邮件发送（可选，用于自动发送激活码）：

```bash
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

对于 Gmail，需要使用应用专用密码：https://myaccount.google.com/apppasswords

### 3. 启动后端服务

```bash
cd /Users/huili/project/XiPackService
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://127.0.0.1:8000 启动

### 4. 访问付费页面

浏览器打开：http://127.0.0.1:8000/static/purchase.html

## API 端点

### 创建订单
```
POST /api/order/create
Content-Type: application/json

{
  "email": "user@example.com",
  "device_id": "DEVICE-UUID-HERE",
  "payment_method": "alipay"  // 或 "wechat"
}
```

### 查询订单状态
```
GET /api/order/status/{order_no}
```

### 验证激活码
```
POST /verify

{
  "license_key": "激活码",
  "device_id": "设备ID"
}
```

### 模拟支付成功（测试用）
```
POST /api/payment/simulate?order_no={订单号}
```

## Swift 应用使用

1. 在 XiPack 应用中点击"激活许可证"按钮
2. 查看设备 ID
3. 点击"购买许可证"按钮，自动跳转到付费页面（设备ID已自动填充）
4. 填写邮箱，选择支付方式
5. 完成支付后，激活码会自动显示并发送到邮箱
6. 复制激活码回到应用中完成激活

## 测试流程

由于这是演示版本，使用"模拟支付成功"按钮来测试完整流程：

1. 访问付费页面
2. 填写设备 ID 和邮箱
3. 选择支付方式
4. 点击"立即购买"
5. 在支付页面点击"🧪 模拟支付成功"按钮
6. 系统会自动生成激活码并显示

## 数据库

系统使用 SQLite 数据库（`licenses.db`），包含以下表：

- **licenses**: 存储激活码信息
  - license_key: 激活码
  - email: 用户邮箱
  - device_id: 绑定的设备ID
  - is_active: 是否激活
  - order_id: 关联的订单号

- **orders**: 存储订单信息
  - order_no: 订单号
  - email: 用户邮箱
  - device_id: 设备ID
  - amount: 支付金额
  - payment_method: 支付方式
  - status: 订单状态（pending/paid/expired/cancelled）
  - trade_no: 支付平台交易号

## 生产环境配置

### 集成真实支付

要集成真实的支付宝/微信支付，需要：

1. 注册支付宝开放平台账号：https://open.alipay.com/
2. 注册微信支付商户：https://pay.weixin.qq.com/
3. 安装支付SDK：
   ```bash
   pip install alipay-sdk-python
   pip install wechatpy
   ```
4. 修改 `main.py` 中的支付相关代码，调用真实的支付API生成二维码

### 邮件服务

推荐使用以下邮件服务：
- Gmail（需要应用专用密码）
- SendGrid（专业邮件服务）
- 阿里云邮件推送
- 腾讯企业邮箱

### 安全配置

1. 使用环境变量存储敏感信息
2. 配置 HTTPS（使用 Nginx + Let's Encrypt）
3. 添加支付签名验证
4. 添加请求频率限制
5. 启用日志记录

## 价格配置

在 [main.py](main.py) 中修改：

```python
LICENSE_PRICE = 99.00  # 修改为你想要的价格
```

## 常见问题

**Q: 邮件发送失败？**  
A: 检查邮箱配置和网络连接，Gmail需要开启"不够安全的应用访问权限"或使用应用专用密码。

**Q: 付费页面打不开？**  
A: 确保后端服务已启动，访问 http://127.0.0.1:8000/static/purchase.html

**Q: 如何查看已生成的激活码？**  
A: 可以直接查询 SQLite 数据库或通过订单号调用 API 查询。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: HTML5 + CSS3 + JavaScript
- **邮件**: Python smtplib
- **支付**: 支付宝/微信扫码支付（待集成）
