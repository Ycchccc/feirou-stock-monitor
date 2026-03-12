# 📈 飞书股票监控助手

**feirou-stock-monitor** - 自动监控 A 股股票，每日收盘后推送持仓日报到飞书。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/os-macos-green.svg)](https://www.apple.com/macos/)

---

## ✨ 功能特性

- 📊 **每日自动推送** - 交易日 16:00 自动发送持仓日报到飞书
- 💰 **持仓盈亏分析** - 实时计算每只股票的盈亏情况
- 📈 **涨跌对比** - 显示与昨日对比、累计收益
- ⚠️ **智能提醒** - 跌幅预警、止盈止损、均线突破提醒
- 📱 **飞书集成** - 直接发送到飞书私信，不错过任何重要信息
- 🔧 **简单易用** - 3 分钟完成安装，一键配置

---

## 🚀 快速开始

### 方式一：一键安装脚本（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/feirou-stock-monitor.git ~/.openclaw/workspace/skills/feirou-stock-monitor

# 2. 进入目录
cd ~/.openclaw/workspace/skills/feirou-stock-monitor

# 3. 运行一键安装
./install.sh

# 4. 修改飞书用户 ID
code ~/.stock_monitor/config.json
# 修改 "user_id": "ou_xxx" 为你的飞书 ID

# 5. 测试运行
python3 daily_with_notify.py
```

### 方式二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/feirou-stock-monitor.git ~/.openclaw/workspace/skills/feirou-stock-monitor

# 2. 安装依赖
cd ~/.openclaw/workspace/skills/feirou-stock-monitor
pip3 install akshare pandas

# 3. 运行配置
python3 quick_setup.py

# 4. 修改飞书用户 ID
code ~/.stock_monitor/config.json

# 5. 加载定时任务
launchctl load ~/Library/LaunchAgents/com.stock-monitor.daily.plist

# 6. 测试
python3 daily_with_notify.py
```

---

## 📋 配置说明

### 1. 配置监控股票

编辑 `~/.stock_monitor/config.json`：

```json
{
  "stocks": [
    {
      "code": "600010",
      "name": "包钢股份",
      "cost": 4.253,
      "shares": 100
    },
    {
      "code": "600519",
      "name": "贵州茅台",
      "cost": 1800.00,
      "shares": 100
    },
    {
      "code": "000858",
      "name": "五 粮 液",
      "cost": 150.00,
      "shares": 200
    }
  ],
  "notify_time": "16:00",
  "user_id": "ou_b5177901cd6463053200000000beb0ed",
  "thresholds": {
    "drop_warn": -5.0,
    "profit_take": 20.0,
    "stop_loss": -15.0
  }
}
```

### 2. 配置字段说明

| 字段 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `stocks[].code` | 股票代码 | ✅ | `600010` |
| `stocks[].name` | 股票名称 | ✅ | `包钢股份` |
| `stocks[].cost` | 成本价 | ✅ | `4.253` |
| `stocks[].shares` | 持股数量 | ✅ | `100` |
| `user_id` | 飞书用户 ID | ✅ | `ou_xxx` |
| `notify_time` | 推送时间 | ❌ | `16:00` |
| `thresholds.drop_warn` | 单日跌幅预警 | ❌ | `-5.0` |
| `thresholds.profit_take` | 累计涨幅止盈 | ❌ | `20.0` |
| `thresholds.stop_loss` | 累计跌幅止损 | ❌ | `-15.0` |

### 3. 获取飞书用户 ID

**方式 1：问机器人**
在飞书中问机器人："我的用户 ID 是什么？"

**方式 2：查看消息**
从飞书消息中获取 `sender_id` 或 `user_id`（格式：`ou_xxx`）

---

## 📊 示例输出

每天 16:00 你会收到这样的飞书消息：

```
📊 股票日报 | 2026-03-12
收盘时间：16:00

📈 涨：2  📉 跌：5  ➖ 平：1

━━━━━━━━━━━━━━━━━━━━
包钢股份 (600010)
  现价：¥2.950  📉-0.34% (-0.010)
  今开：¥2.950  最高：¥2.970  最低：¥2.920
  昨收：¥2.960
  成本：¥4.253 × 100 股
  市值：¥295.00  总成本：¥425.30
  💸 持仓盈亏：¥-130.30 (-30.64%)

────────────────────

中兴通讯 (000063)
  现价：¥37.120  📈+0.00% (0.000)
  今开：¥36.810  最高：¥38.100  最低：¥36.680
  昨收：¥37.120
  成本：¥19.244 × 100 股
  市值：¥3712.00  总成本：¥1924.40
  💰 持仓盈亏：¥+1787.60 (+92.89%)

━━━━━━━━━━━━━━━━━━━━

⚠️ 重要提醒:
  中国一重 (601106): 📉 跌破均线
  中创智领 (688660): 📈 突破均线

━━━━━━━━━━━━━━━━━━━━
长期持有建议：保持耐心，关注基本面
```

---

## 🔧 常用操作

### 查看今日报告
```bash
cat /tmp/stock_report_today.txt
```

### 手动运行一次
```bash
python3 ~/.openclaw/workspace/skills/feirou-stock-monitor/daily_with_notify.py
```

### 查看定时任务状态
```bash
launchctl list | grep stock-monitor
```

### 查看日志
```bash
cat /tmp/stock_monitor.log
cat /tmp/stock_monitor_error.log
```

### 添加新股
编辑 `~/.stock_monitor/config.json`，在 `stocks` 数组中添加新股票。

### 修改推送时间
编辑 `~/.stock_monitor/config.json`，修改 `notify_time` 字段，然后重新运行：
```bash
python3 quick_setup.py
```

---

## ❓ 常见问题

### Q: 收不到日报？

**A:** 按以下步骤排查：
1. 检查定时任务：`launchctl list | grep stock-monitor`
2. 查看日志：`cat /tmp/stock_monitor.log`
3. 手动运行：`python3 daily_with_notify.py`
4. 检查飞书 user_id 是否正确

### Q: 股票数据获取失败？

**A:** 
1. 检查网络连接
2. 更新 akshare：`pip3 install --upgrade akshare`
3. 检查股票代码是否正确

### Q: 飞书消息发送失败？

**A:**
1. 检查 user_id 是否正确（格式：`ou_xxx`）
2. 测试 OpenClaw：`openclaw message send --help`
3. 确认飞书授权正常

### Q: 如何修改成本价？

**A:** 编辑 `~/.stock_monitor/config.json`，找到对应股票，修改 `cost` 字段。

### Q: 如何卸载？

**A:**
```bash
# 卸载定时任务
launchctl unload ~/Library/LaunchAgents/com.stock-monitor.daily.plist

# 删除文件
rm -rf ~/.stock_monitor
rm -rf ~/.openclaw/workspace/skills/feirou-stock-monitor
```

---

## 📁 项目结构

```
feirou-stock-monitor/
├── stock_monitor.py          # 核心：股票数据获取 + 报告生成
├── daily_with_notify.py      # 每日推送（带飞书消息）
├── setup.py                  # 交互式配置向导
├── quick_setup.py            # 快速配置脚本
├── setup_cron.py             # 定时任务安装
├── install.sh                # 一键安装脚本
├── config.json               # 默认配置
├── SKILL.md                  # OpenClaw Skill 文档
├── README.md                 # 本文档
├── INSTALL.md                # 详细安装指南
└── 给新用户的安装说明.md      # 新用户指南
```

**用户数据目录：**
```
~/.stock_monitor/
├── config.json               # 用户配置
├── history.json              # 历史价格数据
└── report_YYYY-MM-DD.json    # 每日报告
```

---

## 🛠️ 技术栈

- **Python 3.8+** - 编程语言
- **akshare** - A 股数据接口
- **pandas** - 数据处理
- **OpenClaw** - Skill 框架
- **macOS launchd** - 定时任务

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 支持

遇到问题？

1. 查看 [常见问题](#-常见问题)
2. 查看日志：`cat /tmp/stock_monitor.log`
3. 提交 Issue
4. 联系开发者

---

## 🎉 致谢

感谢以下开源项目：

- [akshare](https://github.com/akfamily/akshare) - A 股数据接口
- [OpenClaw](https://github.com/openclaw/openclaw) - AI Skill 框架
- [pandas](https://pandas.pydata.org/) - 数据处理库

---

**祝你投资顺利！📈**

*最后更新：2026-03-12*
