# 📦 股票监控助手 - 安装指南

## 快速开始（3 分钟搞定）

### 第 1 步：安装依赖

```bash
pip3 install akshare pandas
```

### 第 2 步：运行配置

```bash
cd ~/.openclaw/workspace/skills/feirou-stock-monitor
python3 quick_setup.py
```

### 第 3 步：修改飞书用户 ID

```bash
# 打开配置文件
code ~/.stock_monitor/config.json

# 找到 user_id 字段，修改为你的飞书用户 ID
# 格式：ou_xxx（可以从飞书消息中获取）
```

**如何获取飞书用户 ID？**
- 方式 1：问我（机器人），我可以帮你查
- 方式 2：在飞书中查看自己的信息
- 方式 3：使用默认值（当前用户的 ID 已配置好）

### 第 4 步：测试运行

```bash
python3 daily_with_notify.py
```

如果看到"✅ 飞书消息发送成功！"，说明配置完成！

---

## 分享给他人的完整流程

### 打包 Skill

```bash
cd ~/.openclaw/workspace/skills/
tar -czf feirou-stock-monitor.tar.gz feirou-stock-monitor/
```

### 发送给他人

通过微信/飞书/邮件发送 `feirou-stock-monitor.tar.gz`

### 他人安装步骤

**1. 解压**
```bash
tar -xzf feirou-stock-monitor.tar.gz -C ~/.openclaw/workspace/skills/
```

**2. 安装依赖**
```bash
cd ~/.openclaw/workspace/skills/feirou-stock-monitor
pip3 install akshare pandas
```

**3. 运行配置**
```bash
python3 quick_setup.py
```

**4. 修改 user_id**
```bash
code ~/.stock_monitor/config.json
# 修改 user_id 为使用者的飞书 ID
```

**5. 测试**
```bash
python3 daily_with_notify.py
```

---

## 配置说明

### 配置文件位置

```
~/.stock_monitor/config.json
```

### 添加新股

编辑配置文件，在 `stocks` 数组中添加：

```json
{
  "code": "600519",
  "name": "贵州茅台",
  "cost": 1800.00,
  "shares": 100
}
```

### 修改成本价

找到对应股票，修改 `cost` 字段：

```json
{
  "code": "600010",
  "name": "包钢股份",
  "cost": 4.253  // ← 修改这里
}
```

---

## 常见问题

**Q: 没有飞书怎么办？**
- 可以修改 `daily_with_notify.py`，改为邮件/微信推送

**Q: 不是 macOS 系统怎么办？**
- Linux：修改 `setup_cron.py` 使用 systemd 或 crontab
- Windows：使用任务计划程序

**Q: 想监控港股/美股怎么办？**
- 修改 `stock_monitor.py` 中的数据源，使用对应的 API

**Q: 收不到消息？**
- 检查 user_id 是否正确
- 查看日志：`cat /tmp/stock_monitor.log`
- 手动运行测试：`python3 daily_with_notify.py`

---

## 技术支持

遇到问题？联系开发者或查看文档：
- 技能文档：`SKILL.md`
- 使用说明：`README.md`
