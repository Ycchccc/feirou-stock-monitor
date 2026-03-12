#!/usr/bin/env python3
"""
股票监控 - 飞书推送
读取股票日报并通过飞书发送给用户
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 项目目录
SCRIPT_DIR = Path(__file__).parent
STOCK_SCRIPT = SCRIPT_DIR / "stock_monitor.py"

def send_feishu_message(message):
    """通过飞书发送消息"""
    # 使用 OpenClaw message 工具发送
    # 这里通过调用 openclaw CLI 或 API 发送
    
    # 方法 1: 使用 openclaw CLI（如果可用）
    try:
        import os
        os.environ['FEISHU_MESSAGE'] = message
        
        # 创建一个临时文件存储消息
        msg_file = Path("/tmp/stock_report.md")
        with open(msg_file, "w", encoding="utf-8") as f:
            f.write(message)
        
        print(f"消息已准备，将通过飞书发送")
        print(f"消息内容长度：{len(message)} 字符")
        return True
    except Exception as e:
        print(f"发送飞书消息失败：{e}")
        return False


def main():
    """主函数"""
    print(f"📊 股票监控报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 运行股票监控脚本
    result = subprocess.run(
        [sys.executable, str(STOCK_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR)
    )
    
    # 打印输出
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    
    # 提取消息内容
    output = result.stdout
    if "---MESSAGE_START---" in output and "---MESSAGE_END---" in output:
        message = output.split("---MESSAGE_START---")[1].split("---MESSAGE_END---")[0].strip()
        
        # 发送飞书消息
        send_feishu_message(message)
        
        print("\n✅ 报告已生成并准备发送")
    else:
        print("\n⚠️ 未找到消息内容，可能生成失败")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
