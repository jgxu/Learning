import os
from dotenv import load_dotenv

# 加载环境变量
# 首先尝试加载系统环境变量中的ENVIRONMENT
environment = os.getenv("ENVIRONMENT", "dev")  # 默认使用开发环境

# 根据环境选择加载对应的配置文件
env_files = {
    "dev": ".env.dev",
    "prod": ".env.prod"
}

# 加载对应的.env文件
load_dotenv(env_files.get(environment, ".env.dev"))

class Settings:
    # 应用配置
    ENVIRONMENT: str = environment
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"mysql+pymysql://root:password@localhost:3306/language_learning_{environment}")
    
    # Gemini API配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # 微信支付配置
    WX_APPID: str = os.getenv("WX_APPID", "your-wechat-appid")
    WX_MCH_ID: str = os.getenv("WX_MCH_ID", "your-wechat-mch-id")
    WX_API_KEY: str = os.getenv("WX_API_KEY", "your-wechat-api-key")
    WX_NOTIFY_URL: str = os.getenv("WX_NOTIFY_URL", f"https://{environment.lower()}-domain.com/payment/notify")
    
    # 订阅价格配置
    SUBSCRIPTION_PRICE: int = 3500  # 单位：分
    SUBSCRIPTION_DURATION: int = 30  # 单位：天
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", f"{environment}-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()