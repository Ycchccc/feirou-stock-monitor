#!/usr/bin/env python3
"""
通过飞书机器人 webhook 发送股票日报

使用方法：
1. 在飞书群或私信中创建机器人
2. 获取 webhook URL
3. 将 webhook URL 保存到 ~/.stock_monitor/webhook.txt
4. 运行此脚本发送消息
"""

import json
import requests
from pathlib import Path

WEBHOOK_FILE = Path.home() / ".stock_monitor" / "webhook.txt"


def send_via_webhook(message: str) -> bool:
    """通过 webhook 发送消息"""
    
    if not WEBHOOK_FILE.exists():
        print(f"❌ 未找到 webhook 配置文件：{WEBHOOK_FILE}")
        print("\n使用方法：")
        print("1. 在飞书中创建机器人，获取 webhook URL")
        print(f"2. 将 URL 保存到：{WEBHOOK_FILE}")
        print("3. 重新运行此脚本")
        return False
    
    with open(WEBHOOK_FILE, "r", encoding="utf-8") as f:
        webhook_url = f.read().strip()
    
    if not webhook_url:
        print("❌ webhook URL 为空")
        return False
    
    # 飞书 webhook 格式
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("StatusCode") == 0 or result.get("code") == 0 or "ok" in str(result).lower():
            print("✅ 飞书消息发送成功！")
            return True
        else:
            print(f"❌ 发送失败：{result}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 网络错误：{e}")
        return False


if __name__ == "__main__":
    # 从标准输入读取消息
    message = sys.stdin.read()
    
    if not message.strip():
        print("❌ 消息为空")
        sys.exit(1)
    
    success = send_via_webhook(message)
    sys.exit(0 if success else 1)
