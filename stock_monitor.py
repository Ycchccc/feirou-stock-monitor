#!/usr/bin/env python3
"""
A 股股票监控工具 - 腾讯 API 版
- 获取股票实时数据（腾讯财经 API）
- 计算收益情况
- 生成日报
- 卖出时机提醒
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 使用腾讯财经 API（稳定可靠）
from tencent_api import get_stock_data_tencent, get_stock_history_tencent

# 数据目录
DATA_DIR = Path.home() / ".stock_monitor"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

# 配置文件
SCRIPT_DIR = Path(__file__).parent
USER_CONFIG_FILE = DATA_DIR / "config.json"
DEFAULT_CONFIG_FILE = SCRIPT_DIR / "config.json"

if USER_CONFIG_FILE.exists():
    CONFIG_FILE = USER_CONFIG_FILE
else:
    CONFIG_FILE = DEFAULT_CONFIG_FILE

# 提醒阈值
THRESHOLDS = {
    "drop_warn": -5.0,      # 单日跌幅预警
    "profit_take": 20.0,    # 累计涨幅止盈
    "stop_loss": -15.0,     # 累计跌幅止损
}


def load_history():
    """加载历史数据"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history):
    """保存历史数据"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_stock_data(code):
    """获取股票实时数据"""
    return get_stock_data_tencent(code)


def get_stock_history(code, days=60):
    """获取股票历史 K 线数据"""
    return get_stock_history_tencent(code, days=days)


def analyze_stock(current_data, history_data):
    """分析股票，给出建议"""
    suggestions = []
    
    if not current_data or not history_data or len(history_data) == 0:
        return suggestions
    
    current_price = current_data["current"]
    change = current_data["change"]
    
    # 获取买入成本（假设以首次监控价格为成本）
    first_close = float(history_data[0].get("close", current_price))
    profit_rate = ((current_price - first_close) / first_close) * 100
    
    # 单日跌幅预警
    if change < THRESHOLDS["drop_warn"]:
        suggestions.append({
            "type": "warn",
            "title": "⚠️ 单日跌幅预警",
            "content": f"今日跌幅 {change:.2f}%，超过 {THRESHOLDS['drop_warn']}% 预警线"
        })
    
    # 累计涨幅止盈
    if profit_rate > THRESHOLDS["profit_take"]:
        suggestions.append({
            "type": "profit",
            "title": "💰 建议止盈",
            "content": f"累计涨幅 {profit_rate:.2f}%，超过 {THRESHOLDS['profit_take']}% 止盈线"
        })
    
    # 累计跌幅止损
    if profit_rate < THRESHOLDS["stop_loss"]:
        suggestions.append({
            "type": "loss",
            "title": "🛑 建议止损",
            "content": f"累计跌幅 {abs(profit_rate):.2f}%，超过 {THRESHOLDS['stop_loss']}% 止损线"
        })
    
    return suggestions


def generate_report(stocks):
    """生成股票日报"""
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "stocks": [],
        "summary": {
            "total": len(stocks),
            "up": 0,
            "down": 0,
            "flat": 0,
        },
        "alerts": [],
    }
    
    history = load_history()
    
    for stock in stocks:
        code = stock["code"]
        print(f"获取 {code} {stock['name']} 数据...")
        
        current_data = get_stock_data(code)
        hist_data = get_stock_history(code, days=60)
        
        if not current_data:
            continue
        
        today_close = current_data["current"]
        yesterday_close = current_data["close"]
        change_rate = current_data["change"]
        
        # 更新统计
        if change_rate > 0:
            report["summary"]["up"] += 1
        elif change_rate < 0:
            report["summary"]["down"] += 1
        else:
            report["summary"]["flat"] += 1
        
        # 计算持仓盈亏
        cost = stock.get("cost", 0)
        shares = stock.get("shares", 0)
        if cost > 0 and shares > 0:
            hold_profit = (today_close - cost) * shares
            hold_profit_rate = ((today_close - cost) / cost) * 100
            market_value = today_close * shares
            cost_total = cost * shares
        else:
            hold_profit = 0
            hold_profit_rate = 0
            market_value = 0
            cost_total = 0
        
        # 分析建议
        suggestions = analyze_stock(current_data, hist_data)
        for s in suggestions:
            s["stock"] = f"{stock['name']}({code})"
            report["alerts"].append(s)
        
        # 保存历史
        stock_history = history.get(code, [])
        stock_history.append({
            "date": report["date"],
            "close": today_close,
            "change": change_rate,
        })
        history[code] = stock_history[-90:]
        
        report["stocks"].append({
            "code": code,
            "name": current_data.get("name", stock["name"]),
            "current": today_close,
            "open": current_data["open"],
            "high": current_data["high"],
            "low": current_data["low"],
            "yesterday": yesterday_close,
            "change": change_rate,
            "change_amount": current_data["change_amount"],
            "volume": current_data["volume"],
            "turnover": current_data["turnover"],
            "cost": cost,
            "shares": shares,
            "hold_profit": hold_profit,
            "hold_profit_rate": hold_profit_rate,
            "market_value": market_value,
            "cost_total": cost_total,
            "date": current_data.get("date", report["date"]),
            "suggestions": suggestions,
        })
    
    save_history(history)
    return report


def format_report_message(report):
    """格式化报告为飞书消息"""
    date = report["date"]
    summary = report["summary"]
    
    lines = [
        f"📊 股票日报 | {date}",
        f"收盘时间：{report['time']}",
        "",
        f"📈 涨：{summary['up']}  📉 跌：{summary['down']}  ➖ 平：{summary['flat']}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    
    for i, stock in enumerate(report["stocks"]):
        change_emoji = "📈" if stock["change"] > 0 else "📉" if stock["change"] < 0 else "➖"
        change_sign = "+" if stock["change"] > 0 else ""
        
        if i > 0:
            lines.append("")
            lines.append("────────────────────")
            lines.append("")
        
        lines.append(f"{stock['name']}({stock['code']})")
        lines.append(f"  现价：¥{stock['current']:.3f}  {change_emoji}{change_sign}{stock['change']:.2f}% ({change_sign}{stock['change_amount']:.3f})")
        lines.append(f"  今开：¥{stock['open']:.3f}  最高：¥{stock['high']:.3f}  最低：¥{stock['low']:.3f}")
        lines.append(f"  昨收：¥{stock['yesterday']:.3f}")
        
        if stock.get("cost", 0) > 0 and stock.get("shares", 0) > 0:
            profit_emoji = "💰" if stock["hold_profit"] > 0 else "💸" if stock["hold_profit"] < 0 else "➖"
            lines.append(f"  成本：¥{stock['cost']:.3f} × {stock['shares']} 股")
            lines.append(f"  市值：¥{stock['market_value']:.2f}  总成本：¥{stock['cost_total']:.2f}")
            lines.append(f"  {profit_emoji} 持仓盈亏：¥{stock['hold_profit']:+.2f}  ({stock['hold_profit_rate']:+.2f}%)")
        
        for s in stock.get("suggestions", []):
            lines.append(f"  ⚠️ {s['title']}: {s['content']}")
    
    if report["alerts"]:
        lines.append("\n━━━━━━━━━━━━━━━━━━━━")
        lines.append("\n⚠️ 重要提醒:")
        for alert in report["alerts"]:
            lines.append(f"  {alert['stock']}: {alert['title']} - {alert['content']}")
    
    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    lines.append("长期持有建议：保持耐心，关注基本面")
    
    return "\n".join(lines)


def main():
    """主函数"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        stocks = config.get("stocks", [])
    else:
        stocks = []
    
    if not stocks:
        print("❌ 未找到股票配置，请编辑 ~/.stock_monitor/config.json")
        sys.exit(1)
    
    print(f"开始生成股票日报...")
    print(f"监控股票：{len(stocks)} 只")
    
    report = generate_report(stocks)
    message = format_report_message(report)
    
    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)
    
    report_file = DATA_DIR / f"report_{report['date']}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n报告已保存：{report_file}")
    
    print("\n---MESSAGE_START---")
    print(message)
    print("---MESSAGE_END---")


if __name__ == "__main__":
    main()
