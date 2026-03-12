#!/bin/bash
# feirou-stock-monitor 一键安装脚本

echo "📈 飞书股票监控助手 - 一键安装"
echo "================================"
echo ""

# 1. 检查 Python
echo "📦 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未安装 Python 3，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 2. 安装依赖
echo ""
echo "📦 安装依赖..."
pip3 install akshare pandas -q
echo "✅ 依赖安装完成"

# 3. 运行配置
echo ""
echo "⚙️  运行配置..."
python3 quick_setup.py

# 4. 提示修改 user_id
echo ""
echo "================================"
echo "⚠️  重要：请修改飞书用户 ID"
echo ""
echo "1. 打开配置文件："
echo "   code ~/.stock_monitor/config.json"
echo ""
echo "2. 找到 user_id 字段，修改为你的飞书 ID"
echo "   格式：ou_xxx"
echo ""
echo "3. 如果不知道你的飞书 ID，可以问机器人帮你查"
echo ""
echo "================================"
echo ""

# 5. 加载定时任务
echo "⏰ 加载定时任务..."
launchctl load ~/Library/LaunchAgents/com.stock-monitor.daily.plist 2>/dev/null
echo "✅ 定时任务已加载"

# 6. 完成
echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "  1. 修改 ~/.stock_monitor/config.json 中的 user_id"
echo "  2. 测试运行：python3 ~/.openclaw/workspace/skills/feirou-stock-monitor/daily_with_notify.py"
echo ""
echo "祝你投资顺利！📈"
echo ""
