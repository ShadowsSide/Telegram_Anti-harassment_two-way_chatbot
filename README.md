# Telegram 双向聊天机器人

一个功能完善的Telegram双向聊天机器人，支持用户与管理员之间的安全、高效通信。

## ✨ 核心特性

### 🎯 话题群组管理
- ✅ 使用Telegram Forum功能，每个用户独立话题
- ✅ 自动显示用户头像、名称、TG ID、用户名
- ✅ 消息自动归类，便于管理

### 🔐 人机验证系统
- ✅ 首次发送消息需通过验证
- ✅ 简单数学题验证，防止机器人骚扰
- ✅ 验证通过后消息才转发给管理员

### ⚡ 并行处理机制
- ✅ 基于asyncio的异步消息队列
- ✅ 多worker并行处理，避免拥堵
- ✅ 支持高并发场景

### 📎 多媒体支持
- ✅ 支持图片、视频、音频、文档
- ✅ Markdown格式双向转发
- ✅ 保持消息格式完整性

### 🤖 AI智能筛选
- ✅ 集成Google Gemini API
- ✅ 自动识别垃圾信息和恶意内容
- ✅ 智能生成解封问题

### 🚫 黑名单管理
- ✅ 管理员可拉黑/解封用户
- ✅ 被拉黑用户收到友好提示
- ✅ AI生成问题，回答正确自动解封

### 👮 权限管理
- ✅ 基于TG ID的管理员验证
- ✅ 支持多管理员
- ✅ 细粒度权限控制

### 💬 用户体验
- ✅ 首次启动友好提示
- ✅ 清晰的状态反馈
- ✅ 自动化解封机制

## 📋 系统要求

- Python 3.10+
- SQLite 3
- Telegram Bot Token
- Google Gemini API Key（可选）
- Telegram Forum/Supergroup

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd telegram-bot
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件，填入实际配置
nano .env
```

必需配置项：
```env
BOT_TOKEN=your_bot_token_here
FORUM_GROUP_ID=-1001234567890
ADMIN_IDS=123456789,987654321
```

可选配置项：
```env
GEMINI_API_KEY=your_gemini_api_key_here
ENABLE_AI_FILTER=true
VERIFICATION_ENABLED=true
```

### 4. 初始化数据库

```bash
python -c "from database.db_manager import DatabaseManager; import asyncio; asyncio.run(DatabaseManager().initialize())"
```

### 5. 运行Bot

```bash
python bot.py
```

## 📖 使用指南

### 获取Bot Token

1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 复制获得的Bot Token

### 创建话题群组

1. 创建一个新的Supergroup
2. 在群组设置中启用"话题"功能
3. 将Bot添加为管理员，授予以下权限：
   - 发送消息
   - 删除消息
   - 管理话题
   - 固定消息

### 获取群组ID

方法1：转发群组消息给 [@userinfobot](https://t.me/userinfobot)

方法2：在Bot代码中添加日志：
```python
print(f"Chat ID: {update.effective_chat.id}")
```

### 获取Gemini API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录Google账号
3. 点击"Create API Key"
4. 复制生成的API密钥

## 🎮 命令列表

### 用户命令

- `/start` - 启动机器人，显示欢迎信息
- `/help` - 显示帮助信息

### 管理员命令

- `/block <user_id> [reason]` - 拉黑用户
- `/unblock <user_id>` - 解封用户
- `/blacklist` - 查看黑名单
- `/stats` - 查看统计信息
- `/broadcast <message>` - 群发消息

## 🏗️ 项目结构

```
telegram-bot/
├── bot.py                    # 主程序入口
├── config.py                 # 配置管理
├── requirements.txt          # 依赖列表
├── database/                 # 数据库模块
│   ├── models.py            # 数据模型
│   └── db_manager.py        # 数据库管理
├── handlers/                 # 消息处理器
│   ├── user_handler.py      # 用户消息
│   ├── admin_handler.py     # 管理员消息
│   └── media_handler.py     # 媒体处理
├── services/                 # 业务服务
│   ├── verification.py      # 验证服务
│   ├── gemini_service.py    # AI服务
│   ├── blacklist.py         # 黑名单管理
│   └── queue_manager.py     # 队列管理
└── utils/                    # 工具函数
    ├── decorators.py        # 装饰器
    ├── helpers.py           # 辅助函数
    └── logger.py            # 日志配置
```

详细结构请查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📚 文档

- [架构设计](ARCHITECTURE.md) - 系统架构和技术选型
- [实现计划](IMPLEMENTATION_PLAN.md) - 详细的开发计划
- [数据库设计](DATABASE_DESIGN.md) - 数据库表结构和操作
- [API集成](API_INTEGRATION.md) - Telegram和Gemini API使用
- [项目结构](PROJECT_STRUCTURE.md) - 完整的文件结构说明

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `BOT_TOKEN` | Telegram Bot Token | ✅ | - |
| `FORUM_GROUP_ID` | 话题群组ID | ✅ | - |
| `ADMIN_IDS` | 管理员ID列表（逗号分隔） | ✅ | - |
| `GEMINI_API_KEY` | Gemini API密钥 | ❌ | - |
| `ENABLE_AI_FILTER` | 启用AI筛选 | ❌ | true |
| `VERIFICATION_ENABLED` | 启用人机验证 | ❌ | true |
| `AUTO_UNBLOCK_ENABLED` | 启用自动解封 | ❌ | true |
| `DATABASE_PATH` | 数据库路径 | ❌ | ./data/bot.db |
| `MAX_WORKERS` | 队列worker数量 | ❌ | 5 |

完整配置请参考 [.env.example](.env.example)

## 🐳 Docker部署

### 使用Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 使用Docker

```bash
# 构建镜像
docker build -t telegram-bot .

# 运行容器
docker run -d \
  --name telegram-bot \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  telegram-bot
```

## 🔒 安全建议

1. **保护API密钥**
   - 不要将`.env`文件提交到版本控制
   - 使用环境变量或密钥管理服务

2. **限制管理员权限**
   - 只添加信任的用户为管理员
   - 定期审查管理员列表

3. **数据备份**
   - 定期备份数据库
   - 使用自动备份脚本

4. **监控日志**
   - 定期检查错误日志
   - 设置异常告警

5. **更新依赖**
   - 定期更新Python包
   - 关注安全公告

## 🐛 故障排查

### Bot无法启动

1. 检查Bot Token是否正确
2. 确认网络连接正常
3. 查看错误日志：`tail -f logs/error.log`

### 消息无法发送

1. 确认Bot在群组中有管理员权限
2. 检查群组ID是否正确
3. 验证用户是否被拉黑

### 数据库错误

1. 检查数据库文件权限
2. 确认磁盘空间充足
3. 尝试重新初始化数据库

### Gemini API错误

1. 验证API密钥是否有效
2. 检查API配额是否用完
3. 查看网络连接状态

更多问题请查看 [Issues](https://github.com/your-repo/issues)

## 📊 性能优化

- ✅ 异步IO操作，避免阻塞
- ✅ 数据库连接池复用
- ✅ 消息队列并行处理
- ✅ 速率限制防止API超限
- ✅ 缓存频繁查询数据

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 开发计划

- [x] 基础框架搭建
- [x] 话题群组功能
- [x] 人机验证系统
- [x] 黑名单管理
- [x] AI集成
- [ ] 多语言支持
- [ ] Web管理面板
- [ ] 消息统计分析
- [ ] 自动回复模板

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- 您的名字 - [@your_telegram](https://t.me/your_telegram)

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - 优秀的Telegram Bot框架
- [Google Gemini](https://ai.google.dev/) - 强大的AI能力
- 所有贡献者

## 📞 联系方式

- Telegram: [@your_telegram](https://t.me/your_telegram)
- Email: your.email@example.com
- Issues: [GitHub Issues](https://github.com/your-repo/issues)

## ⭐ Star History

如果这个项目对你有帮助，请给个Star⭐️

---

**注意**: 本项目仅供学习交流使用，请遵守Telegram服务条款和当地法律法规。