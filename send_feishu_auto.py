#!/usr/bin/env python3
"""
股票监控日报 - 自动发送到飞书
使用飞书 API 直接发送，无需 webhook
"""

import json
import subprocess
import sys
import requests
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent
STOCK_SCRIPT = SCRIPT_DIR / "stock_monitor.py"
CREDENTIALS_DIR = Path.home() / ".openclaw" / "credentials" / "feishu" / "main"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

# 飞书 API
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"


def get_feishu_credentials():
    """获取飞书凭证"""
    # 从 openclaw.json 获取
    with open(OPENCLAW_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    account = config["channels"]["feishu"]["accounts"]["main"]
    return {
        "app_id": account["appId"],
        "app_secret": account["appSecret"]
    }


def get_access_token(app_id: str, app_secret: str) -> str:
    """获取飞书 access token"""
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    r = requests.post(url, json=payload, timeout=10)
    result = r.json()
    
    if result.get("code") == 0:
        return result["tenant_access_token"]
    else:
        raise Exception(f"获取 token 失败：{result}")


def send_message(token: str, user_id: str, message: str):
    """发送飞书消息"""
    # 使用正确的 API 端点
    url = f"{FEISHU_API_BASE}/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 使用文本消息
    payload = {
        "receive_id": user_id,
        "msg_type": "text",
        "content": json.dumps({"text": message}, ensure_ascii=False)
    }
    
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    result = r.json()
    
    if result.get("code") == 0:
        return True
    else:
        raise Exception(f"发送失败：{result}")


def get_stock_report():
    """获取股票报告"""
    result = subprocess.run(
        ["python3", str(STOCK_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    output = result.stdout
    if "---MESSAGE_START---" not in output:
        return None
    
    message = output.split("---MESSAGE_START---")[1].split("---MESSAGE_END---")[0].strip()
    return message


def main():
    print("📊 股票日报自动发送")
    print("=" * 50)
    
    # 1. 获取股票报告
    print("1️⃣ 获取股票报告...")
    message = get_stock_report()
    if not message:
        print("❌ 获取报告失败")
        sys.exit(1)
    print("✅ 报告获取成功")
    
    # 2. 获取飞书凭证
    print("2️⃣ 获取飞书凭证...")
    try:
        creds = get_feishu_credentials()
        print(f"   App ID: {creds['app_id']}")
    except Exception as e:
        print(f"❌ 获取凭证失败：{e}")
        sys.exit(1)
    
    # 3. 获取 access token
    print("3️⃣ 获取 access token...")
    try:
        token = get_access_token(creds["app_id"], creds["app_secret"])
        print("✅ Token 获取成功")
    except Exception as e:
        print(f"❌ Token 获取失败：{e}")
        sys.exit(1)
    
    # 4. 获取用户 ID
    print("4️⃣ 获取用户 ID...")
    config_file = Path.home() / ".stock_monitor" / "config.json"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            stock_config = json.load(f)
        user_id = stock_config.get("user_id", "")
    else:
        user_id = ""
    
    if not user_id or user_id == "请修改为你的飞书用户 ID（格式：ou_xxx）":
        print("❌ 用户 ID 未配置，请在 ~/.stock_monitor/config.json 中设置 user_id")
        sys.exit(1)
    
    print(f"   用户 ID: {user_id}")
    
    # 5. 发送消息（添加测试标记）
    print("5️⃣ 发送飞书消息...")
    try:
        send_message(token, user_id, message)
        print("✅ 发送成功！")
    except Exception as e:
        print(f"❌ 发送失败：{e}")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 完成！")


if __name__ == "__main__":
    main()
