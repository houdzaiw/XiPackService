# XiPackService
XiPack 打包工具的激活码管理后端服务

## 快速启动

### 方法 1：使用启动脚本（推荐）

```bash
cd /Users/huili/project/XiPackService
./start_server.sh
```

### 方法 2：手动启动

```bash
cd /Users/huili/project/XiPackService
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**注意**：不要使用 `uvicorn` 命令，而是使用 `python3 -m uvicorn`

## 访问地址

- 🛒 **付费页面**: http://127.0.0.1:8000/static/purchase.html
- 📖 **API 文档**: http://127.0.0.1:8000/docs
- 🔧 **API 根路径**: http://127.0.0.1:8000

## 功能特性

- ✅ 订单创建和管理
- ✅ 支付宝/微信支付支持（演示版本）
- ✅ 自动生成激活码
- ✅ 邮件发送激活码
- ✅ 设备绑定验证
- ✅ 激活码验证 API

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 环境变量配置（可选）

配置邮件服务以自动发送激活码：

```bash
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

## 更多文档

详细配置和使用说明请查看 [PAYMENT_SETUP.md](PAYMENT_SETUP.md)