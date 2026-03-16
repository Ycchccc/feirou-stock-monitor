#!/usr/bin/env python3
"""
腾讯财经 API 数据获取模块
替代 akshare，解决连接问题
"""

import requests
from datetime import datetime


def get_stock_data_tencent(code):
    """
    通过腾讯财经 API 获取股票数据
    使用 K 线 API 获取最新数据（更可靠）
    
    :param code: 股票代码 (如 600010, 000063)
    :return: 股票数据字典，失败返回 None
    """
    try:
        # 判断市场
        if code.startswith('6') or code.startswith('688'):
            market = "sh"
        elif code.startswith('0') or code.startswith('3'):
            market = "sz"
        else:
            print(f"  未知市场代码：{code}")
            return None
        
        # 使用 K 线 API 获取最新数据（更可靠）
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{code},day,,,2,qfq"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("code") != 0 or not data.get("data"):
            print(f"  获取 {code} 数据失败：API 返回错误")
            return None
        
        stock_data = data["data"].get(f"{market}{code}")
        if not stock_data:
            print(f"  获取 {code} 数据失败：无数据")
            return None
        
        klines = stock_data.get("qfqday", [])
        
        if not klines or len(klines) < 2:
            print(f"  获取 {code} 数据失败：K 线数据不足")
            return None
        
        # 最新一天数据
        latest = klines[-1]
        yesterday = klines[-2]
        
        # kline 格式：[日期，开盘，收盘，最高，最低，成交量]
        current = float(latest[2]) if latest[2] else 0  # 收盘
        open_price = float(latest[1]) if latest[1] else 0  # 开盘
        high = float(latest[3]) if latest[3] else 0  # 最高
        low = float(latest[4]) if latest[4] else 0  # 最低
        volume = float(latest[5]) if latest[5] else 0  # 成交量
        
        yesterday_close = float(yesterday[2]) if yesterday[2] else current  # 昨收
        
        # 计算涨跌幅
        if yesterday_close > 0:
            change = ((current - yesterday_close) / yesterday_close) * 100
            change_amount = current - yesterday_close
        else:
            change = 0
            change_amount = 0
        
        # 获取股票名称（通过另一个 API）
        name = code
        try:
            name_url = f"https://qt.gtimg.cn/q={market}{code}"
            name_resp = requests.get(name_url, headers=headers, timeout=5)
            if name_resp.status_code == 200:
                # 返回格式：v_{market}{code}="51~中兴通讯~000063~..."
                content = name_resp.text
                if '~' in content:
                    parts = content.split('~')
                    if len(parts) > 1:
                        name = parts[1]
        except:
            pass
        
        return {
            "code": code,
            "name": name,
            "current": current,
            "open": open_price,
            "high": high,
            "low": low,
            "close": yesterday_close,
            "change": change,
            "change_amount": change_amount,
            "volume": volume,
            "turnover": volume * current,  # 估算成交额
            "date": latest[0] if latest[0] else datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
        }
        
    except requests.RequestException as e:
        print(f"  获取 {code} 数据网络错误：{e}")
        return None
    except Exception as e:
        print(f"  获取 {code} 数据失败：{e}")
        return None


def get_stock_history_tencent(code, days=60):
    """
    通过腾讯财经 API 获取股票历史 K 线数据
    
    :param code: 股票代码
    :param days: 获取天数
    :return: 简化的历史数据列表，失败返回 None
    """
    try:
        # 判断市场
        if code.startswith('6') or code.startswith('688'):
            market = "sh"
        elif code.startswith('0') or code.startswith('3'):
            market = "sz"
        else:
            return None
        
        # 腾讯 K 线 API
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{code},day,,,500,qfq"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("code") != 0 or not data.get("data"):
            return None
        
        stock_data = data["data"].get(f"{market}{code}")
        if not stock_data:
            return None
        
        klines = stock_data.get("qfqday", [])
        
        # 转换为简单的字典列表
        history = []
        for kline in klines[-days:]:
            # kline 格式：[日期，开盘，收盘，最高，最低，成交量]
            if len(kline) >= 6:
                history.append({
                    "date": kline[0],
                    "open": float(kline[1]) if kline[1] else 0,
                    "close": float(kline[2]) if kline[2] else 0,
                    "high": float(kline[3]) if kline[3] else 0,
                    "low": float(kline[4]) if kline[4] else 0,
                    "volume": float(kline[5]) if kline[5] else 0,
                })
        
        return history
        
    except Exception as e:
        print(f"  获取 {code} 历史数据失败：{e}")
        return None


if __name__ == "__main__":
    # 测试
    test_codes = ["600010", "000063", "300264"]
    
    for code in test_codes:
        print(f"\n测试 {code}:")
        data = get_stock_data_tencent(code)
        if data:
            print(f"  名称：{data['name']}")
            print(f"  现价：{data['current']}")
            print(f"  涨跌：{data['change']:.2f}%")
            print(f"  日期：{data['date']}")
        else:
            print(f"  获取失败")
        
        history = get_stock_history_tencent(code, days=5)
        if history:
            print(f"  历史数据：{len(history)} 条")
            print(f"  最近：{history[-1]}")
