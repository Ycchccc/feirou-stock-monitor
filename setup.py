#!/usr/bin/env python3
"""
股票监控 Skill - 配置向导
帮助用户快速配置监控股票和定时任务
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# 配置目录
CONFIG_DIR = Path.home() / ".stock_monitor"
CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "stocks": [],
    "notify_time": "16:00",
    "user_id": "",
    "thresholds": {
        "drop_warn": -5.0,
        "profit_take": 20.0,
        "stop_loss": -15.0
    }
}


def print_header(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)


def input_stock():
    """输入一只股票信息"""
    print("\n请输入股票信息：")
    
    code = input("  股票代码 (如 600010): ").strip()
    if not code:
        return None
    
    name = input("  股票名称 (如 包钢股份): ").strip()
    
    cost = input("  成本价 (如 4.253): ").strip()
    try:
        cost = float(cost)
    except ValueError:
        print("  ⚠️ 成本价格式错误，使用 0")
        cost = 0
    
    shares = input("  持股数量 (如 100): ").strip()
    try:
        shares = int(shares)
    except ValueError:
        print("  ⚠️ 持股数量格式错误，使用 0")
        shares = 0
    
    return {
        "code": code,
        "name": name,
        "cost": cost,
        "shares": shares
    }


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 配置已保存：{CONFIG_FILE}")


def get_feishu_user_id():
    """获取当前用户的飞书 ID"""
    # 尝试从 OpenClaw 环境获取
    user_id = os.environ.get("FEISHU_USER_ID", "")
    
    if not user_id:
        # 尝试从消息上下文获取（如果有）
        print("\n💡 请输入你的飞书用户 ID（格式：ou_xxx）")
        print("   如果不知道，可以留空，稍后在 config.json 中手动填写")
        user_id = input("  飞书用户 ID: ").strip()
    
    return user_id


def install_dependencies():
    """安装依赖"""
    print("\n📦 正在安装依赖...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "akshare", "pandas", "-q"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ 依赖安装完成")
    else:
        print(f"⚠️ 依赖安装失败：{result.stderr}")
        print("   请手动运行：pip3 install akshare pandas")


def install_cron():
    """安装定时任务"""
    print("\n⏰ 正在安装定时任务...")
    
    script_dir = Path(__file__).parent
    cron_script = script_dir / "setup_cron.py"
    
    if cron_script.exists():
        result = subprocess.run(
            [sys.executable, str(cron_script)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ {result.stderr}")
    else:
        print("⚠️ 未找到 setup_cron.py")


def main():
    """主函数"""
    print_header("📈 股票监控助手 - 配置向导")
    
    # 1. 检查依赖
    try:
        import akshare
        import pandas
        print("✅ 依赖已安装")
    except ImportError:
        install = input("\n⚠️ 未安装依赖，是否现在安装？(y/n): ").strip().lower()
        if install == 'y':
            install_dependencies()
        else:
            print("⚠️ 请手动安装：pip3 install akshare pandas")
    
    # 2. 加载或创建配置
    config = load_config()
    
    if config["stocks"]:
        print(f"\n📋 当前已配置 {len(config['stocks'])} 只股票:")
        for s in config["stocks"]:
            print(f"   {s['code']} {s['name']} (成本：¥{s['cost']}, {s['shares']}股)")
        
        action = input("\n操作：[A]添加股票 [R]重新配置 [Q]退出: ").strip().upper()
        if action == 'Q':
            print("👋 已退出")
            return
        elif action == 'R':
            config = DEFAULT_CONFIG.copy()
    
    # 3. 输入股票
    print("\n" + "=" * 50)
    print("  添加监控股票")
    print("=" * 50)
    print("\n💡 提示：可以一次添加多只股票，输入空股票代码结束")
    
    while True:
        stock = input_stock()
        if not stock:
            break
        config["stocks"].append(stock)
        print(f"✅ 已添加：{stock['code']} {stock['name']}")
    
    if not config["stocks"]:
        print("\n⚠️ 至少需要添加一只股票！")
        return
    
    # 4. 设置飞书用户 ID
    print_header("飞书推送设置")
    
    if not config.get("user_id"):
        user_id = get_feishu_user_id()
        if user_id:
            config["user_id"] = user_id
            print(f"✅ 飞书用户 ID: {user_id}")
    else:
        print(f"✅ 飞书用户 ID: {config['user_id']}")
        change = input("\n是否修改？(y/n): ").strip().lower()
        if change == 'y':
            config["user_id"] = get_feishu_user_id()
    
    # 5. 设置推送时间
    print(f"\n当前推送时间：{config.get('notify_time', '16:00')}")
    change_time = input("是否修改推送时间？(y/n): ").strip().lower()
    if change_time == 'y':
        new_time = input("请输入推送时间 (格式 HH:MM，如 16:00): ").strip()
        config["notify_time"] = new_time
    
    # 6. 保存配置
    print_header("保存配置")
    save_config(config)
    
    # 7. 安装定时任务
    print_header("安装定时任务")
    install = input("\n是否现在安装定时任务？(y/n): ").strip().lower()
    if install == 'y':
        install_cron()
    
    # 8. 测试运行
    print_header("测试运行")
    test = input("\n是否立即运行一次测试？(y/n): ").strip().lower()
    if test == 'y':
        script_dir = Path(__file__).parent
        test_script = script_dir / "daily_with_notify.py"
        
        if test_script.exists():
            print("\n🚀 正在运行测试...")
            result = subprocess.run(
                [sys.executable, str(test_script)],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(f"错误：{result.stderr}")
        else:
            print("⚠️ 未找到测试脚本")
    
    # 完成
    print_header("配置完成")
    print("\n✅ 股票监控助手已配置完成！")
    print("\n接下来：")
    print("  1. 每个交易日 16:00 自动推送日报")
    print("  2. 查看日志：cat /tmp/stock_monitor.log")
    print("  3. 修改配置：code ~/.stock_monitor/config.json")
    print("  4. 手动运行：python3 ~/.openclaw/workspace/skills/stock-monitor/daily_with_notify.py")
    print("\n📊 祝你投资顺利！")
    print()


if __name__ == "__main__":
    main()
