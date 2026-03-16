#!/usr/bin/env python3
"""
股票监控日报 - 生成报告
每天 16:00 运行，生成报告并保存

发送方式（任选其一）：
1. 飞书 webhook - 配置 ~/.stock_monitor/webhook.txt
2. OpenClaw message 工具 - 在飞书中运行 /stock 命令
3. 手动查看 - 查看 /tmp/stock_monitor.log
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
STOCK_SCRIPT = SCRIPT_DIR / "stock_monitor.py"
DATA_DIR = Path.home() / ".stock_monitor"
LOG_FILE = Path("/tmp/stock_monitor.log")


def run_stock_monitor():
    """运行股票监控脚本"""
    print("📊 生成股票日报...")
    python_path = "/usr/local/bin/python3"
    
    result = subprocess.run(
        [python_path, str(STOCK_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    # 记录日志
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(result.stdout)
        if result.stderr:
            f.write("\n---ERROR---\n")
            f.write(result.stderr)
    
    print(f"✅ 日志已保存：{LOG_FILE}")
    
    # 提取消息
    output = result.stdout
    if "---MESSAGE_START---" not in output:
        print("❌ 报告生成失败")
        print(output)
        return None
    
    message = output.split("---MESSAGE_START---")[1].split("---MESSAGE_END---")[0].strip()
    return message


def send_via_webhook(message: str) -> bool:
    """通过飞书 webhook 发送"""
    webhook_file = DATA_DIR / "webhook.txt"
    
    if not webhook_file.exists():
        return False
    
    with open(webhook_file, "r", encoding="utf-8") as f:
        webhook_url = f.read().strip()
    
    if not webhook_url:
        return False
    
    import requests
    payload = {
        "msg_type": "text",
        "content": {"text": message}
    }
    
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        result = r.json()
        if result.get("StatusCode") == 0 or result.get("code") == 0:
            print("✅ 通过 webhook 发送成功！")
            return True
    except:
        pass
    
    return False


def main():
    message = run_stock_monitor()
    
    if not message:
        sys.exit(1)
    
    # 尝试通过 webhook 发送
    if send_via_webhook(message):
        sys.exit(0)
    
    # webhook 不可用时，只保存日志
    print("\n💡 飞书推送未配置，可选择以下方式查看报告：")
    print(f"  1. 查看日志：cat {LOG_FILE}")
    print("  2. 在飞书中运行：python3 stock_monitor.py")
    print("  3. 配置 webhook：将飞书机器人 webhook URL 保存到 ~/.stock_monitor/webhook.txt")
    
    # 保存消息到临时文件
    msg_file = Path("/tmp/stock_report_today.txt")
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(message)
    print(f"\n📄 报告已保存：{msg_file}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
