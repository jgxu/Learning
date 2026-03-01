from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uvicorn
import os
import logging
import traceback

# 首先初始化日志系统
from utils.logging import app_logger

# 导入其他模块
from config import settings
from models import Base, engine
from dependencies.auth import get_current_user, get_db
from services import user_service, document_service, ai_service, srs_service, payment_service
from schemas import user as user_schemas
from schemas import document as document_schemas
from schemas import vocabulary as vocabulary_schemas
from schemas import srs_record as srs_schemas
from schemas import payment as payment_schemas

# 设置根日志级别
logging.basicConfig(level=logging.INFO)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="语言学习小程序后端API",
    description="企业级语言学习小程序后端系统，基于FastAPI构建",
    version="1.0.0"
)

# 全局异常处理

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理，捕获所有未处理的异常"""
    # 记录详细的错误日志
    error_traceback = traceback.format_exc()
    app_logger.error(f"全局异常 - 请求路径: {request.url.path}, 错误: {str(exc)}, 堆栈信息: {error_traceback}")
    
    # 返回友好的错误响应
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "details": str(exc) if settings.DEBUG else None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理"""
    app_logger.warning(f"HTTP异常 - 请求路径: {request.url.path}, 状态码: {exc.status_code}, 错误信息: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "details": None
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """ValueError异常处理"""
    app_logger.warning(f"ValueError异常 - 请求路径: {request.url.path}, 错误信息: {str(exc)}")
    
    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "message": str(exc),
            "details": None
        }
    )

# 数据库异常处理
try:
    from sqlalchemy.exc import SQLAlchemyError
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """SQLAlchemy数据库异常处理"""
        app_logger.error(f"数据库异常 - 请求路径: {request.url.path}, 错误: {str(exc)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "数据库操作失败，请稍后重试",
                "details": str(exc) if settings.DEBUG else None
            }
        )
except ImportError:
    # 如果未安装SQLAlchemy，跳过此异常处理
    pass

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为微信小程序域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户相关路由
@app.get("/user/profile", 
         response_model=user_schemas.UserProfile,
         tags=["用户管理"],
         summary="获取用户个人信息",
         description="获取当前用户的个人信息，包括昵称、头像、订阅状态和学习统计数据")
async def get_user_profile(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.get_user_profile(db, current_user.openid)

@app.post("/user/settings", 
          response_model=user_schemas.UserSettings,
          tags=["用户管理"],
          summary="更新用户设置",
          description="更新用户的每日复习量设置，范围为20-100个单词")
async def update_user_settings(
    settings: user_schemas.UserSettingsUpdate,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.update_user_settings(db, current_user.openid, settings)

# 文档相关路由
@app.post("/document/upload", 
          response_model=document_schemas.Document,
          tags=["文档管理"],
          summary="上传文档",
          description="支持上传Word、PDF、TXT、图片或链接，系统会自动解析内容并存储")
async def upload_document(
    file: Optional[UploadFile] = File(None, description="上传的文件"),
    link: Optional[str] = Query(None, description="文档链接地址"),
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file and not link:
        raise HTTPException(status_code=400, detail="必须提供文件或链接")
    return document_service.upload_document(db, current_user.openid, file, link)

@app.get("/document/history", 
         response_model=List[document_schemas.Document],
         tags=["文档管理"],
         summary="获取文档上传历史",
         description="分页获取用户上传的所有文档历史记录")
async def get_document_history(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量，1-100"),
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return document_service.get_document_history(db, current_user.openid, page, page_size)

# AI相关路由
@app.post("/ai/analyze-word", 
          response_model=vocabulary_schemas.WordAnalysis,
          tags=["AI分析"],
          summary="分析单词",
          description="使用AI分析单词，返回音标、中文释义和例句")
async def analyze_word(
    request: vocabulary_schemas.AnalyzeWordRequest,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ai_service.analyze_word(db, current_user.openid, request.word)

@app.post("/ai/translate-sentence", 
          response_model=vocabulary_schemas.SentenceTranslation,
          tags=["AI分析"],
          summary="翻译句子",
          description="使用AI翻译句子，返回准确的中文翻译")
async def translate_sentence(
    request: vocabulary_schemas.TranslateSentenceRequest,
    current_user: user_schemas.User = Depends(get_current_user)
):
    return ai_service.translate_sentence(request.sentence)

# 学习/复习相关路由
@app.get("/srs/review-list", 
         response_model=List[srs_schemas.ReviewItem],
         tags=["学习复习"],
         summary="获取今日复习列表",
         description="获取今日到期需要复习的单词列表，基于SRS算法计算")
async def get_review_list(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return srs_service.get_today_review_list(db, current_user.openid)

@app.post("/srs/submit-feedback", 
          response_model=srs_schemas.SRSRecord,
          tags=["学习复习"],
          summary="提交复习反馈",
          description="提交单词复习反馈（认识/模糊/忘记），系统会根据反馈更新SRS参数")
async def submit_feedback(
    request: srs_schemas.FeedbackRequest,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return srs_service.submit_feedback(db, current_user.openid, request)

@app.post("/learn/sync-duration", 
          response_model=dict,
          tags=["学习复习"],
          summary="同步学习时长",
          description="同步本次学习的时长，单位为秒")
async def sync_learning_duration(
    request: vocabulary_schemas.LearningDuration,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.sync_learning_duration(db, current_user.openid, request.duration)

# 支付相关路由
@app.post("/payment/create-order", 
          response_model=payment_schemas.PaymentOrder,
          tags=["支付管理"],
          summary="创建支付订单",
          description="创建微信支付订阅订单，用于购买月卡服务（35元/月）")
async def create_payment_order(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return payment_service.create_subscription_order(db, current_user.openid)

# 健康检查接口
@app.get("/health", tags=["系统管理"])
async def health_check():
    """健康检查接口，用于监控应用状态"""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

# 打印启动环境配置
app_logger.info("="*60)
app_logger.info("语言学习小程序后端服务启动")
app_logger.info(f"环境配置：")
app_logger.info(f"- 环境名称: {settings.ENVIRONMENT}")
app_logger.info(f"- 调试模式: {settings.DEBUG}")
# 隐藏数据库密码
if settings.DATABASE_URL:
    import re
    db_url = re.sub(r'(?<=:)[^:@]+(?=@)', '******', settings.DATABASE_URL)
    app_logger.info(f"- 数据库URL: {db_url}")
app_logger.info(f"- Gemini模型: {settings.GEMINI_MODEL}")
app_logger.info(f"- 微信AppID: {settings.WX_APPID}")
app_logger.info(f"- 监听端口: 80")
app_logger.info("="*60)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)