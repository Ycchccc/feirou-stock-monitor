#!/usr/bin/env python3
"""
股票监控日报 - 每日自动运行
生成报告并通过飞书发送
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
STOCK_SCRIPT = SCRIPT_DIR / "stock_monitor.py"

def main():
    print(f"🚀 运行股票监控日报 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行股票监控脚本
    result = subprocess.run(
        [sys.executable, str(STOCK_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    output = result.stdout
    
    # 提取消息内容
    if "---MESSAGE_START---" in output and "---MESSAGE_END---" in output:
        message = output.split("---MESSAGE_START---")[1].split("---MESSAGE_END---")[0].strip()
        
        # 保存消息到文件（用于飞书推送）
        msg_file = Path("/tmp/stock_report.txt")
        with open(msg_file, "w", encoding="utf-8") as f:
            f.write(message)
        
        print(f"\n✅ 报告已生成：{msg_file}")
        print(f"消息长度：{len(message)} 字符")
        
        # 输出消息内容供外部读取
        print("\n" + "=" * 50)
        print(message)
        print("=" * 50)
        
    else:
        print("\n⚠️ 报告生成失败")
        print(output)
        if result.stderr:
            print("错误:", result.stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
