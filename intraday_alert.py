#!/usr/bin/env python3
"""
盘中预警 - 实时监控股票，触发阈值时推送飞书
- 跌破止损线预警
- 涨破止盈线提醒
- 单日大跌预警
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from tencent_api import get_stock_data_tencent

# 配置
SCRIPT_DIR = Path(__file__).parent
USER_CONFIG = Path.home() / ".stock_monitor" / "config.json"
HISTORY_FILE = Path.home() / ".stock_monitor" / "alert_history.json"


def load_config():
    """加载配置"""
    if USER_CONFIG.exists():
        with open(USER_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_alert_history():
    """加载今日预警历史（避免重复推送）"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_alert_history(history):
    """保存预警历史"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def check_alerts(stock, data, config):
    """检查预警条件"""
    alerts = []
    thresholds = config.get("thresholds", {})
    
    cost = stock.get("cost", 0)
    current = data.get("current", 0)
    change = data.get("change", 0)
    
    if cost <= 0 or current <= 0:
        return alerts
    
    # 持仓盈亏比例
    profit_rate = ((current - cost) / cost) * 100
    
    # 1. 单日跌幅预警
    drop_warn = thresholds.get("drop_warn", -5.0)
    if change <= drop_warn:
        alerts.append({
            "type": "drop_warn",
            "level": "⚠️",
            "title": f"单日大跌预警",
            "message": f"{stock['name']} 今日跌幅 {change:.2f}%，已跌破 {drop_warn}% 预警线",
        })
    
    # 2. 止损预警
    stop_loss = thresholds.get("stop_loss", -15.0)
    if profit_rate <= stop_loss:
        alerts.append({
            "type": "stop_loss",
            "level": "🛑",
            "title": f"止损线预警",
            "message": f"{stock['name']} 累计亏损 {abs(profit_rate):.2f}%，已触及 {stop_loss}% 止损线",
        })
    
    # 3. 止盈提醒
    profit_take = thresholds.get("profit_take", 20.0)
    if profit_rate >= profit_take:
        alerts.append({
            "type": "profit_take",
            "level": "💰",
            "title": f"止盈线提醒",
            "message": f"{stock['name']} 累计盈利 {profit_rate:.2f}%，已达 {profit_take}% 止盈线",
        })
    
    return alerts


def format_alert_message(alerts):
    """格式化预警消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"🚨 盘中预警 | {now}",
        "",
        "━" * 30,
    ]
    
    for alert in alerts:
        lines.append("")
        lines.append(f"{alert['level']} {alert['title']}")
        lines.append(f"   {alert['message']}")
    
    lines.append("")
    lines.append("━" * 30)
    lines.append("请及时关注，理性决策")
    
    return "\n".join(lines)


def send_feishu_message(message, user_id):
    """发送飞书消息"""
    import requests
    
    OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
    
    with open(OPENCLAW_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    account = config["channels"]["feishu"]["accounts"]["main"]
    app_id = account["appId"]
    app_secret = account["appSecret"]
    
    # 获取 token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    r = requests.post(token_url, json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
    token = r.json().get("tenant_access_token")
    
    if not token:
        print("获取 token 失败")
        return False
    
    # 发送消息
    msg_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "receive_id": user_id,
        "msg_type": "text",
        "content": json.dumps({"text": message}, ensure_ascii=False)
    }
    
    r = requests.post(msg_url, headers=headers, json=payload, timeout=10)
    return r.json().get("code") == 0


def main():
    """主函数"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 检查是否在交易时间（9:30-11:30, 13:00-15:00）
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    morning = (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute < 30)
    afternoon = (hour == 13) or (hour == 14)
    
    if not (morning or afternoon):
        print(f"非交易时间，跳过检查 ({now.strftime('%H:%M')})")
        return
    
    # 加载配置
    config = load_config()
    stocks = config.get("stocks", [])
    user_id = config.get("user_id", "")
    
    if not stocks or not user_id:
        print("配置不完整")
        return
    
    # 加载今日预警历史
    history = load_alert_history()
    today_history = history.get(today, {})
    
    all_alerts = []
    
    for stock in stocks:
        code = stock["code"]
        print(f"检查 {stock['name']}({code})...")
        
        data = get_stock_data_tencent(code)
        if not data:
            print(f"  获取数据失败")
            continue
        
        alerts = check_alerts(stock, data, config)
        
        for alert in alerts:
            alert_key = f"{code}_{alert['type']}"
            
            # 同一股票同一类型预警，每小时最多发一次
            if alert_key in today_history:
                last_time = today_history[alert_key]
                last_hour = int(last_time.split(":")[0])
                current_hour = now.hour
                
                if last_hour == current_hour:
                    print(f"  {alert['title']} - 本小时已推送，跳过")
                    continue
            
            alert["stock"] = stock["name"]
            alert["code"] = code
            all_alerts.append(alert)
            
            # 记录推送时间
            today_history[alert_key] = now.strftime("%H:%M")
    
    # 发送预警
    if all_alerts:
        message = format_alert_message(all_alerts)
        print("\n" + message)
        
        if send_feishu_message(message, user_id):
            print("\n✅ 预警已发送")
        else:
            print("\n❌ 发送失败")
    else:
        print("无预警")
    
    # 保存历史
    history[today] = today_history
    save_alert_history(history)


if __name__ == "__main__":
    main()