#!/usr/bin/env python3
"""
快速配置脚本 - 复制默认配置到用户目录
"""

import json
import shutil
from pathlib import Path

# 源配置（脚本目录）
SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG = SCRIPT_DIR / "config.json"

# 目标配置（用户目录）
USER_CONFIG_DIR = Path.home() / ".stock_monitor"
USER_CONFIG_DIR.mkdir(exist_ok=True)
USER_CONFIG = USER_CONFIG_DIR / "config.json"

def main():
    print("📈 股票监控助手 - 快速配置\n")
    
    # 检查默认配置
    if not DEFAULT_CONFIG.exists():
        print("❌ 未找到默认配置文件")
        return 1
    
    # 复制配置
    if USER_CONFIG.exists():
        print(f"⚠️ 用户配置已存在：{USER_CONFIG}")
        action = input("是否覆盖？(y/n): ").strip().lower()
        if action != 'y':
            print("👋 已取消")
            return 0
    
    # 读取默认配置
    with open(DEFAULT_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 提示用户修改 user_id
    print("\n💡 请修改配置文件中的 user_id 为你的飞书用户 ID")
    print(f"   配置文件：{USER_CONFIG}")
    print(f"   当前 user_id: {config.get('user_id', '')}")
    
    # 保存配置（不修改 user_id，让用户自己改）
    with open(USER_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 配置已复制到：{USER_CONFIG}")
    
    # 安装定时任务
    print("\n⏰ 安装定时任务...")
    cron_script = SCRIPT_DIR / "setup_cron.py"
    if cron_script.exists():
        import subprocess
        result = subprocess.run(
            ["python3", str(cron_script)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    
    print("\n✅ 配置完成！")
    print("\n下一步：")
    print(f"  1. 编辑配置文件：code {USER_CONFIG}")
    print(f"  2. 修改 user_id 为你的飞书用户 ID")
    print(f"  3. 测试运行：python3 {SCRIPT_DIR}/daily_with_notify.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
