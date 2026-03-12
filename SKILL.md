---
name: feirou-stock-monitor
description: A 股股票自动监控，每日收盘后推送持仓日报到飞书，支持盈亏分析、卖出提醒
icon: 📈
os: macos
tools: akshare, pandas
install: pip install akshare pandas
tags: stock, finance, feishu, monitoring
---

# 📈 飞书股票监控助手 (feirou-stock-monitor)

自动监控 A 股股票，每日收盘后推送持仓日报到飞书。

## 功能

- 📊 **每日日报** — 收盘后 30 分钟自动推送
- 💰 **持仓盈亏** — 实时计算每只股票的盈亏
- 📈 **涨跌分析** — 与昨日对比、累计收益
- ⚠️ **智能提醒** — 跌幅预警、止盈止损、均线突破
- 📱 **飞书推送** — 直接发送到你的飞书私信

## 快速开始

### 1. 安装 Skill

```bash
# 方式 1：通过 clawhub（推荐）
npx clawhub install feirou-stock-monitor

# 方式 2：手动克隆
git clone https://github.com/YOUR_REPO/feirou-stock-monitor.git ~/.openclaw/workspace/skills/feirou-stock-monitor
```

### 2. 安装依赖

```bash
cd ~/.openclaw/workspace/skills/feirou-stock-monitor
pip3 install akshare pandas
```

### 3. 配置监控股票

运行配置向导：

```bash
python3 setup.py
```

或手动编辑 `~/.stock_monitor/config.json`：

```json
{
  "stocks": [
    {"code": "600010", "name": "包钢股份", "cost": 4.253, "shares": 100},
    {"code": "600050", "name": "中国联通", "cost": 7.811, "shares": 100}
  ],
  "notify_time": "16:00",
  "user_id": "ou_xxx"
}
```

### 4. 安装定时任务

```bash
python3 setup.py install-cron
```

### 5. 测试运行

```bash
python3 stock_monitor.py
```

## 配置说明

### 股票配置

| 字段 | 说明 | 示例 |
|------|------|------|
| code | 股票代码 | `600010` |
| name | 股票名称 | `包钢股份` |
| cost | 成本价 | `4.253` |
| shares | 持股数量 | `100` |

### 提醒阈值（可选）

```json
{
  "thresholds": {
    "drop_warn": -5.0,      // 单日跌幅预警
    "profit_take": 20.0,    // 累计涨幅止盈
    "stop_loss": -15.0      // 累计跌幅止损
  }
}
```

## 常用命令

```bash
# 查看今日报告
python3 stock_monitor.py

# 手动发送飞书消息
python3 daily_with_notify.py

# 查看定时任务状态
launchctl list | grep feirou-stock-monitor

# 查看日志
cat /tmp/stock_monitor.log

# 卸载定时任务
python3 setup.py uninstall-cron
```

## 文件结构

```
~/.openclaw/workspace/skills/feirou-stock-monitor/
├── stock_monitor.py          # 核心脚本
├── daily_with_notify.py      # 每日推送
├── setup.py                  # 配置向导
├── config.json               # 默认配置
└── SKILL.md                  # 本文档

~/.stock_monitor/
├── config.json               # 用户配置
├── history.json              # 历史数据
└── report_YYYY-MM-DD.json    # 每日报告
```

## 多用户支持

每个用户的配置独立存储在 `~/.stock_monitor/config.json`，互不干扰。

## 问题排查

**Q: 收不到日报？**
- 检查定时任务：`launchctl list | grep feirou-stock-monitor`
- 查看日志：`cat /tmp/stock_monitor.log`
- 手动运行：`python3 daily_with_notify.py`

**Q: 股票数据获取失败？**
- 检查网络
- 更新 akshare：`pip3 install --upgrade akshare`

**Q: 飞书消息发送失败？**
- 检查 user_id 是否正确
- 测试 openclaw message：`openclaw message send --help`

## 许可证

MIT
