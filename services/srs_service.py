from sqlalchemy.orm import Session
from models import SRSRecord, Vocabulary, User
from schemas.srs_record import FeedbackRequest, ReviewItem, FeedbackType
from datetime import datetime, timedelta


def get_today_review_list(db: Session, openid: str) -> list[ReviewItem]:
    """获取今日到期需复习的单词列表"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise ValueError("用户不存在")
    
    # 获取今日到期的SRS记录
    today = datetime.utcnow().date()
    srs_records = db.query(SRSRecord).filter(
        SRSRecord.user_id == user.id,
        SRSRecord.next_review_date <= datetime.utcnow()
    ).limit(user.daily_goal).all()
    
    # 构建复习列表
    review_list = []
    for record in srs_records:
        if record.vocabulary:
            review_list.append(ReviewItem(
                srs_record_id=record.id,
                word=record.vocabulary.word,
                phonetic=record.vocabulary.phonetic,
                translation=record.vocabulary.translation
            ))
    
    return review_list


def submit_feedback(db: Session, openid: str, request: FeedbackRequest) -> SRSRecord:
    """提交单词复习反馈，更新SRS参数"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise ValueError("用户不存在")
    
    # 获取SRS记录
    srs_record = db.query(SRSRecord).filter(
        SRSRecord.id == request.srs_record_id,
        SRSRecord.user_id == user.id
    ).first()
    
    if not srs_record:
        raise ValueError("SRS记录不存在")
    
    # 根据反馈类型更新SRS参数
    if request.feedback == FeedbackType.HARD:
        # 忘记：重新开始学习
        srs_record.repetitions = 0
        srs_record.easiness_factor = max(1.3, srs_record.easiness_factor - 0.2)
        srs_record.interval = 1
    elif request.feedback == FeedbackType.MEDIUM:
        # 模糊：降低难度系数，缩短间隔
        srs_record.repetitions = max(0, srs_record.repetitions - 1)
        srs_record.easiness_factor = max(1.3, srs_record.easiness_factor - 0.1)
        srs_record.interval = max(1, srs_record.interval // 2)
    elif request.feedback == FeedbackType.EASY:
        # 认识：增加重复次数，调整难度系数，延长间隔
        srs_record.repetitions += 1
        srs_record.easiness_factor = max(1.3, srs_record.easiness_factor + 0.1)
        
        if srs_record.repetitions == 1:
            srs_record.interval = 1
        elif srs_record.repetitions == 2:
            srs_record.interval = 6
        else:
            srs_record.interval = int(srs_record.interval * srs_record.easiness_factor)
    
    # 更新复习日期
    srs_record.last_review_date = datetime.utcnow()
    srs_record.next_review_date = datetime.utcnow() + timedelta(days=srs_record.interval)
    
    db.commit()
    db.refresh(srs_record)
    
    return srs_record


def add_word_to_srs(db: Session, user_id: int, vocabulary_id: int) -> SRSRecord:
    """将单词添加到SRS系统"""
    # 检查是否已存在
    existing_record = db.query(SRSRecord).filter(
        SRSRecord.user_id == user_id,
        SRSRecord.vocabulary_id == vocabulary_id
    ).first()
    
    if existing_record:
        return existing_record
    
    # 创建新的SRS记录
    srs_record = SRSRecord(
        user_id=user_id,
        vocabulary_id=vocabulary_id,
        easiness_factor=2.5,
        interval=1,
        repetitions=0,
        next_review_date=datetime.utcnow()
    )
    
    db.add(srs_record)
    db.commit()
    db.refresh(srs_record)
    
    return srs_record