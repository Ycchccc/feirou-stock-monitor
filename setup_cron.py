#!/usr/bin/env python3
"""
安装股票监控股票的定时任务
每天 16:00 运行（A 股收盘后 30 分钟），工作日执行
"""

import os
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CRON_FILE = Path("/tmp/stock_monitor_cron")

def install():
    """安装定时任务"""
    script_path = SCRIPT_DIR / "run_daily.py"
    
    # macOS 使用 launchd
    notify_script = SCRIPT_DIR / "daily_with_notify.py"
    python_path = "/usr/local/bin/python3"  # 使用正确的 Python 路径
    
    launchd_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stock-monitor.daily</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{notify_script.absolute()}</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>16</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{SCRIPT_DIR.absolute()}</string>
    
    <key>StandardOutPath</key>
    <string>/tmp/stock_monitor.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/stock_monitor_error.log</string>
</dict>
</plist>
"""
    
    plist_file = Path.home() / "Library/LaunchAgents/com.stock-monitor.daily.plist"
    plist_file.parent.mkdir(exist_ok=True)
    
    with open(plist_file, "w", encoding="utf-8") as f:
        f.write(launchd_plist)
    
    print(f"✅ 已创建 launchd 配置文件：{plist_file}")
    print("\n现在运行以下命令加载定时任务：")
    print(f"  launchctl load {plist_file}")
    print("\n查看状态：")
    print(f"  launchctl list | grep stock-monitor")
    print("\n卸载：")
    print(f"  launchctl unload {plist_file}")
    
    return True

def uninstall():
    """卸载定时任务"""
    plist_file = Path.home() / "Library/LaunchAgents/com.stock-monitor.daily.plist"
    
    if plist_file.exists():
        print(f"请运行以下命令卸载：")
        print(f"  launchctl unload {plist_file}")
        print(f"  rm {plist_file}")
    else:
        print("未找到已安装的定时任务")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "uninstall":
            uninstall()
        else:
            print("用法：python setup_cron.py [install|uninstall]")
    else:
        install()
