import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Settings:
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/language_learning")
    
    # Gemini API配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # 微信支付配置
    WX_APPID: str = os.getenv("WX_APPID", "your-wechat-appid")
    WX_MCH_ID: str = os.getenv("WX_MCH_ID", "your-wechat-mch-id")
    WX_API_KEY: str = os.getenv("WX_API_KEY", "your-wechat-api-key")
    WX_NOTIFY_URL: str = os.getenv("WX_NOTIFY_URL", "https://your-domain.com/payment/notify")
    
    # 订阅价格配置
    SUBSCRIPTION_PRICE: int = 3500  # 单位：分
    SUBSCRIPTION_DURATION: int = 30  # 单位：天
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()