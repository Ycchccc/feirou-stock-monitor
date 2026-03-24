#!/usr/bin/env python3
"""
通过飞书 API 发送股票日报
使用已配置的飞书机器人账号发送消息
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 股票监控脚本
SCRIPT_DIR = Path(__file__).parent
STOCK_SCRIPT = SCRIPT_DIR / "stock_monitor.py"

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


def send_via_openclaw(message: str) -> bool:
    """通过 OpenClaw 发送（需要配置）"""
    # 这个方法需要 OpenClaw 支持
    # 暂时返回 False，使用下面的手动方法
    return False


def main():
    print("📊 获取股票日报...")
    message = get_stock_report()
    
    if not message:
        print("❌ 获取报告失败")
        sys.exit(1)
    
    print("✅ 报告获取成功！")
    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)
    
    print("\n💡 要自动发送到飞书，请配置以下方式之一：")
    print("  1. 飞书 webhook：创建 ~/.stock_monitor/webhook.txt")
    print("  2. 使用 OpenClaw 的 message 工具")
    print("  3. 在飞书中直接运行：python3 stock_monitor.py")
    
    # 保存报告
    report_file = Path("/tmp/stock_report_" + datetime.now().strftime("%Y-%m-%d") + ".txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(message)
    print(f"\n📄 报告已保存：{report_file}")


if __name__ == "__main__":
    main()
