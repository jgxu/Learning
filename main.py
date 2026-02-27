from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os

from config import settings
from models import Base, engine
from dependencies.auth import get_current_user, get_db
from services import user_service, document_service, ai_service, srs_service, payment_service
from schemas import user as user_schemas
from schemas import document as document_schemas
from schemas import vocabulary as vocabulary_schemas
from schemas import srs_record as srs_schemas
from schemas import payment as payment_schemas

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="语言学习小程序后端API",
    description="企业级语言学习小程序后端系统，基于FastAPI构建",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为微信小程序域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户相关路由
@app.get("/user/profile", response_model=user_schemas.UserProfile)
async def get_user_profile(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.get_user_profile(db, current_user.openid)

@app.post("/user/settings", response_model=user_schemas.UserSettings)
async def update_user_settings(
    settings: user_schemas.UserSettingsUpdate,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.update_user_settings(db, current_user.openid, settings)

# 文档相关路由
@app.post("/document/upload", response_model=document_schemas.Document)
async def upload_document(
    file: Optional[UploadFile] = File(None),
    link: Optional[str] = Query(None),
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file and not link:
        raise HTTPException(status_code=400, detail="必须提供文件或链接")
    return document_service.upload_document(db, current_user.openid, file, link)

@app.get("/document/history", response_model=List[document_schemas.Document])
async def get_document_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return document_service.get_document_history(db, current_user.openid, page, page_size)

# AI相关路由
@app.post("/ai/analyze-word", response_model=vocabulary_schemas.WordAnalysis)
async def analyze_word(
    request: vocabulary_schemas.AnalyzeWordRequest,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ai_service.analyze_word(db, current_user.openid, request.word)

@app.post("/ai/translate-sentence", response_model=vocabulary_schemas.SentenceTranslation)
async def translate_sentence(
    request: vocabulary_schemas.TranslateSentenceRequest,
    current_user: user_schemas.User = Depends(get_current_user)
):
    return ai_service.translate_sentence(request.sentence)

# 学习/复习相关路由
@app.get("/srs/review-list", response_model=List[srs_schemas.ReviewItem])
async def get_review_list(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return srs_service.get_today_review_list(db, current_user.openid)

@app.post("/srs/submit-feedback", response_model=srs_schemas.SRSRecord)
async def submit_feedback(
    request: srs_schemas.FeedbackRequest,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return srs_service.submit_feedback(db, current_user.openid, request)

@app.post("/learn/sync-duration", response_model=dict)
async def sync_learning_duration(
    request: vocabulary_schemas.LearningDuration,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.sync_learning_duration(db, current_user.openid, request.duration)

# 支付相关路由
@app.post("/payment/create-order", response_model=payment_schemas.PaymentOrder)
async def create_payment_order(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return payment_service.create_subscription_order(db, current_user.openid)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/