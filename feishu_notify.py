#!/usr/bin/env python3
"""
股票监控 - 飞书消息推送
读取生成的报告并发送到飞书
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def send_to_feishu(message):
    """使用 OpenClaw message 工具发送飞书消息"""
    
    # 从用户配置读取 user_id
    user_config_file = Path.home() / ".stock_monitor" / "config.json"
    if user_config_file.exists():
        with open(user_config_file, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        user_id = user_config.get("user_id", "")
    else:
        user_id = ""
    
    if not user_id:
        print("❌ 错误：未配置飞书 user_id")
        print("请编辑 ~/.stock_monitor/config.json，设置 user_id 为你的飞书 ID（格式：ou_xxx）")
        return False
    
    # 保存消息到临时文件
    msg_file = Path("/tmp/stock_feishu_msg.txt")
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(message)
    
    print(f"消息已保存到：{msg_file}")
    print(f"接收者：{user_id}")
    
    # 使用 openclaw message 命令发送（如果可用）
    cmd = f"""openclaw message send --channel=feishu --target="user:{user_id}" --message=@{msg_file}"""
    
    print(f"\n发送命令：{cmd}")
    print("\n或者手动复制以下内容发送到飞书：")
    print("=" * 60)
    print(message)
    print("=" * 60)
    
    return True

def main():
    # 读取最新报告
    report_file = Path.home() / ".stock_monitor" / f"report_{datetime.now().strftime('%Y-%m-%d')}.json"
    
    if not report_file.exists():
        # 尝试运行股票监控脚本
        print("今日报告尚未生成，正在生成...")
        script_dir = Path(__file__).parent
        subprocess.run([sys.executable, str(script_dir / "run_daily.py")])
    
    if report_file.exists():
        import json
        with open(report_file, "r", encoding="utf-8") as f:
            report = json.load(f)
        
        # 生成消息
        from stock_monitor import format_report_message
        message = format_report_message(report)
        
        # 发送
        send_to_feishu(message)
    else:
        print("❌ 未找到报告文件")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
