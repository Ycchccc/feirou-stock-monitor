#!/usr/bin/env python3
"""
A 股股票监控工具
- 获取股票实时数据
- 计算收益情况
- 生成日报
- 卖出时机提醒
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("请先安装依赖：pip install akshare pandas")
    sys.exit(1)

# 数据目录
DATA_DIR = Path.home() / ".stock_monitor"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

# 配置文件（优先使用用户配置，fallback 到脚本目录的默认配置）
SCRIPT_DIR = Path(__file__).parent
USER_CONFIG_FILE = DATA_DIR / "config.json"  # 用户配置
DEFAULT_CONFIG_FILE = SCRIPT_DIR / "config.json"  # 默认配置

# 优先使用用户配置
if USER_CONFIG_FILE.exists():
    CONFIG_FILE = USER_CONFIG_FILE
else:
    CONFIG_FILE = DEFAULT_CONFIG_FILE

# 默认监控列表
DEFAULT_STOCKS = [
    {"code": "600010", "name": "包钢股份"},
    {"code": "600050", "name": "中国联通"},
    {"code": "300264", "name": "佳都科技"},
    {"code": "601106", "name": "中国一重"},
    {"code": "688660", "name": "中创智领"},
    {"code": "000063", "name": "中兴通讯"},
    {"code": "600222", "name": "海南海药"},
    {"code": "300398", "name": "爱康科技"},
]

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
    """获取股票实时数据（通过历史 K 线获取最新数据）"""
    try:
        # 获取历史行情（包含最新交易日数据）
        df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date='20260101')
        
        if df is None or len(df) == 0:
            print(f"  获取 {code} 历史数据失败")
            return None
        
        # 获取最新一行数据
        latest = df.iloc[-1]
        yesterday = df.iloc[-2] if len(df) > 1 else latest
        
        return {
            "code": code,
            "name": code,  # 历史数据中没有名称
            "current": float(latest.get("收盘", 0)),
            "open": float(latest.get("开盘", 0)),
            "high": float(latest.get("最高", 0)),
            "low": float(latest.get("最低", 0)),
            "close": float(yesterday.get("收盘", latest.get("收盘", 0))),  # 昨收
            "change": float(latest.get("涨跌幅", 0)),
            "change_amount": float(latest.get("涨跌额", 0)),
            "volume": float(latest.get("成交量", 0)),
            "turnover": float(latest.get("成交额", 0)),
            "market_cap": 0,  # 历史数据中没有市值
            "pe": 0,  # 历史数据中没有市盈率
            "date": latest.get("日期", ""),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"获取 {code} 数据失败：{e}")
        return None


def get_stock_history(code, days=30):
    """获取股票历史 K 线数据"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"))
        return df
    except Exception as e:
        print(f"获取 {code} 历史数据失败：{e}")
        return None


def analyze_stock(current_data, history_data):
    """分析股票，给出建议"""
    suggestions = []
    
    if not current_data or history_data is None or len(history_data) == 0:
        return suggestions
    
    current_price = current_data["current"]
    change = current_data["change"]
    
    # 获取买入成本（假设以首次监控价格为成本）
    first_close = float(history_data.iloc[-1]["收盘"]) if len(history_data) > 0 else current_price
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
    
    # 技术分析
    if len(history_data) >= 20:
        # 计算 20 日均线
        ma20 = history_data["收盘"].rolling(window=20).mean().iloc[-1]
        if current_price < ma20 * 0.95:
            suggestions.append({
                "type": "info",
                "title": "📉 跌破均线",
                "content": f"当前价格低于 20 日均线 {((ma20 - current_price) / ma20 * 100):.2f}%"
            })
        elif current_price > ma20 * 1.05:
            suggestions.append({
                "type": "info",
                "title": "📈 突破均线",
                "content": f"当前价格高于 20 日均线 {((current_price - ma20) / ma20 * 100):.2f}%"
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
        history_data = get_stock_history(code, days=60)
        
        if not current_data:
            continue
        
        # 计算与昨日相比
        yesterday_close = current_data["close"]
        today_close = current_data["current"]
        change_rate = current_data["change"]
        
        # 更新统计
        if change_rate > 0:
            report["summary"]["up"] += 1
        elif change_rate < 0:
            report["summary"]["down"] += 1
        else:
            report["summary"]["flat"] += 1
        
        # 计算持仓盈亏（使用配置中的成本价）
        cost = stock.get("cost", 0)
        shares = stock.get("shares", 0)
        if cost > 0 and shares > 0:
            hold_profit = (today_close - cost) * shares  # 持仓盈亏金额
            hold_profit_rate = ((today_close - cost) / cost) * 100  # 持仓盈亏比例
            market_value = today_close * shares  # 当前市值
            cost_total = cost * shares  # 总成本
        else:
            hold_profit = 0
            hold_profit_rate = 0
            market_value = 0
            cost_total = 0
        
        # 获取历史数据
        stock_history = history.get(code, [])
        
        # 分析建议
        suggestions = analyze_stock(current_data, history_data)
        for s in suggestions:
            s["stock"] = f"{stock['name']}({code})"
            report["alerts"].append(s)
        
        # 保存历史
        stock_history.append({
            "date": report["date"],
            "close": today_close,
            "change": change_rate,
        })
        # 保留最近 90 天
        history[code] = stock_history[-90:]
        
        report["stocks"].append({
            "code": code,
            "name": stock["name"],
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
            "pe": current_data.get("pe", 0),
            "date": current_data.get("date", report["date"]),
            "suggestions": suggestions,
        })
    
    save_history(history)
    
    # 转换所有 numpy/pandas 类型为 Python 原生类型
    def convert_value(v):
        if hasattr(v, 'item'):  # numpy 类型
            return v.item()
        elif isinstance(v, dict):
            return {k: convert_value(val) for k, val in v.items()}
        elif isinstance(v, list):
            return [convert_value(item) for item in v]
        return v
    
    report = convert_value(report)
    
    return report


def format_report_message(report):
    """格式化报告为飞书消息"""
    date = report["date"]
    summary = report["summary"]
    
    # 标题
    lines = [
        f"📊 股票日报 | {date}",
        f"收盘时间：{report['time']}",
        "",
        f"📈 涨：{summary['up']}  📉 跌：{summary['down']}  ➖ 平：{summary['flat']}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
    ]
    
    # 股票详情
    for i, stock in enumerate(report["stocks"]):
        change_emoji = "📈" if stock["change"] > 0 else "📉" if stock["change"] < 0 else "➖"
        change_color = "+" if stock["change"] > 0 else ""
        
        # 每只股票之间加分割线
        if i > 0:
            lines.append("")
            lines.append("────────────────────")
            lines.append("")
        
        lines.append(f"{stock['name']}({stock['code']})")
        lines.append(f"  现价：¥{stock['current']:.3f}  {change_emoji}{change_color}{stock['change']:.2f}% ({change_color}{stock['change_amount']:.3f})")
        lines.append(f"  今开：¥{stock['open']:.3f}  最高：¥{stock['high']:.3f}  最低：¥{stock['low']:.3f}")
        lines.append(f"  昨收：¥{stock['yesterday']:.3f}")
        
        # 持仓信息
        if stock.get("cost", 0) > 0 and stock.get("shares", 0) > 0:
            profit_emoji = "💰" if stock["hold_profit"] > 0 else "💸" if stock["hold_profit"] < 0 else "➖"
            lines.append(f"  成本：¥{stock['cost']:.3f} × {stock['shares']} 股")
            lines.append(f"  市值：¥{stock['market_value']:.2f}  总成本：¥{stock['cost_total']:.2f}")
            lines.append(f"  {profit_emoji} 持仓盈亏：¥{stock['hold_profit']:+.2f}  ({stock['hold_profit_rate']:+.2f}%)")
        
        if stock.get("pe", 0) > 0:
            lines.append(f"  市盈率：{stock['pe']:.2f}")
        
        # 提醒
        for s in stock.get("suggestions", []):
            lines.append(f"  ⚠️ {s['title']}: {s['content']}")
    
    # 重要提醒
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
    # 加载配置
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        stocks = config.get("stocks", DEFAULT_STOCKS)
    else:
        stocks = DEFAULT_STOCKS
    
    print(f"开始生成股票日报...")
    print(f"监控股票：{len(stocks)} 只")
    
    report = generate_report(stocks)
    message = format_report_message(report)
    
    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)
    
    # 保存报告（使用 str 转换所有非标准类型）
    report_file = DATA_DIR / f"report_{report['date']}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n报告已保存：{report_file}")
    
    # 输出消息（用于管道传递给飞书）
    print("\n---MESSAGE_START---")
    print(message)
    print("---MESSAGE_END---")


if __name__ == "__main__":
    main()
