# 语言学习小程序后端系统

这是一个基于FastAPI构建的企业级语言学习小程序后端系统，集成了MySQL数据库、Gemini AI引擎和微信支付功能。

## 功能模块

### 1. 精读模块
- 支持上传多种格式文件：Word、PDF、TXT、图片和链接
- 集成Gemini AI进行内容解析
- 实现单词和句子的智能分析

### 2. 复习模块
- 基于SRS（间隔重复）算法的智能复习系统
- 支持用户反馈：认识、模糊、忘记
- 动态计算下次复习时间

### 3. 用户与支付模块
- 基于微信云托管的用户身份识别
- 支持每日复习量设置（20-100）
- 微信支付订阅功能（35元/月）
- 学习时长统计

## 技术栈

- **后端框架**：FastAPI
- **数据库**：MySQL + SQLAlchemy ORM
- **AI引擎**：Gemini 1.5 Pro
- **部署环境**：微信云托管
- **API文档**：Swagger UI自动生成

## 快速开始

### 1. 环境准备

- Python 3.10+
- MySQL 5.7+
- 微信云托管账号
- Google Gemini API密钥

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

修改`.env`文件，填写以下配置：

```
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/language_learning

# Gemini API配置
GEMINI_API_KEY=your-gemini-api-key

# 微信支付配置
WX_APPID=your-wechat-appid
WX_MCH_ID=your-wechat-mch-id
WX_API_KEY=your-wechat-api-key
WX_NOTIFY_URL=https://your-domain.com/payment/notify

# 应用配置
SECRET_KEY=your-secret-key-for-jwt
```

### 4. 运行应用

```bash
# 开发模式
uvicorn main:app --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 80
```

### 5. 访问API文档

运行应用后，访问以下地址查看API文档：
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## API接口

### 用户相关
- `GET /user/profile` - 获取个人信息及订阅状态
- `POST /user/settings` - 更新每日复习量设置

### 文档相关
- `POST /document/upload` - 上传文件并返回解析文本
- `GET /document/history` - 分页获取上传历史

### AI相关
- `POST /ai/analyze-word` - 分析单词，返回释义、发音、例句
- `POST /ai/translate-sentence` - 翻译句子

### 学习/复习相关
- `GET /srs/review-list` - 获取今日到期需复习的单词列表
- `POST /srs/submit-feedback` - 提交单词复习反馈
- `POST /learn/sync-duration` - 同步本次学习时长

### 支付相关
- `POST /payment/create-order` - 创建微信支付订单

## 部署到微信云托管

1. 构建Docker镜像：
   ```bash
docker build -t language-learning-backend .
```

2. 按照微信云托管的部署指南上传镜像并配置服务

3. 设置环境变量（在微信云托管控制台中）

## 项目结构

```
.
├── main.py              # 主应用入口
├── config.py            # 配置文件
├── models.py            # 数据库模型
├── dependencies/
│   └── auth.py          # 身份验证和数据库依赖
├── schemas/
│   ├── user.py          # 用户相关Schema
│   ├── document.py      # 文档相关Schema
│   ├── vocabulary.py    # 词汇相关Schema
│   ├── srs_record.py    # SRS相关Schema
│   └── payment.py       # 支付相关Schema
├── services/
│   ├── user_service.py      # 用户服务
│   ├── document_service.py  # 文档服务
│   ├── ai_service.py        # AI服务
│   ├── srs_service.py       # SRS服务
│   └── payment_service.py   # 支付服务
├── requirements.txt     # 依赖列表
├── Dockerfile           # Docker配置
├── .env                 # 环境变量
└── uploads/             # 文件上传目录
```

## 注意事项

1. 首次运行时会自动创建数据库表
2. 确保MySQL服务已启动并可访问
3. 替换.env文件中的所有占位符为实际值
4. 微信支付配置需要在微信商户平台完成申请

## 许可证

MIT# Learning
