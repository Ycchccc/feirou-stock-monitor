#!/usr/bin/env python3
"""
股票监控日报 - 带飞书推送
每天 16:00 运行，生成报告并发送到飞书
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
STOCK_SCRIPT = SCRIPT_DIR / "stock_monitor.py"
DATA_DIR = Path.home() / ".stock_monitor"

def get_today_report():
    """获取今日报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = DATA_DIR / f"report_{today}.json"
    
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def send_feishu_report():
    """发送飞书报告"""
    # 先运行股票监控脚本生成报告
    print("📊 生成股票日报...")
    result = subprocess.run(
        [sys.executable, str(STOCK_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    # 提取消息
    output = result.stdout
    if "---MESSAGE_START---" not in output or "---MESSAGE_END---" not in output:
        print("❌ 报告生成失败")
        print(output)
        return False
    
    message = output.split("---MESSAGE_START---")[1].split("---MESSAGE_END---")[0].strip()
    
    # 保存报告到临时文件
    msg_file = Path("/tmp/stock_report_today.txt")
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(message)
    
    print(f"✅ 报告已生成：{msg_file}")
    print(f"消息长度：{len(message)} 字符")
    
    # 使用 OpenClaw message 工具发送
    # 从用户配置读取 user_id
    user_config_file = Path.home() / ".stock_monitor" / "config.json"
    if user_config_file.exists():
        with open(user_config_file, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        user_id = user_config.get("user_id", "")
    else:
        user_id = ""  # 需要在配置文件中设置
    
    if not user_id:
        print("❌ 错误：未配置飞书 user_id")
        print("请编辑 ~/.stock_monitor/config.json，设置 user_id 为你的飞书 ID（格式：ou_xxx）")
        return 1
    
    print(f"\n📤 正在发送到飞书...")
    
    # 调用 openclaw message 命令
    cmd = [
        "openclaw", "message", "send",
        "--channel=feishu",
        f"--target=user:{user_id}",
        f"--message={message}"
    ]
    
    try:
        msg_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if msg_result.returncode == 0:
            print("✅ 飞书消息发送成功！")
            return True
        else:
            print(f"❌ 发送失败：{msg_result.stderr}")
            # 如果自动发送失败，提供手动方案
            print(f"\n💡 请手动复制以下内容发送到飞书：")
            print("=" * 60)
            print(message)
            print("=" * 60)
            return False
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        print(f"\n💡 请手动复制以下内容发送到飞书：")
        print("=" * 60)
        print(message)
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = send_feishu_report()
    sys.exit(0 if success else 1)
