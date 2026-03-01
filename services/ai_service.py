import os
import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from models import Vocabulary
from schemas.vocabulary import WordAnalysis, Example, SentenceTranslation
from config import settings
from datetime import datetime
from utils.logging import app_logger

# 配置Gemini API
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
genai.configure()
model = genai.GenerativeModel(settings.GEMINI_MODEL)


def analyze_word(db: Session, user_id: str, word: str) -> WordAnalysis:
    """分析单词，返回释义、发音、例句"""
    app_logger.info(f"分析单词，用户ID: {user_id}，单词: {word}")
    
    # 检查缓存
    cached_vocab = db.query(Vocabulary).filter(
        Vocabulary.user_id == user_id,
        Vocabulary.word == word
    ).first()
    
    if cached_vocab:
        # 如果有缓存，直接返回
        app_logger.info(f"从缓存获取单词分析结果，用户ID: {user_id}，单词: {word}")
        examples = json.loads(cached_vocab.examples) if cached_vocab.examples else []
        return WordAnalysis(
            word=cached_vocab.word,
            phonetic=cached_vocab.phonetic,
            translation=cached_vocab.translation,
            examples=[Example(**ex) for ex in examples]
        )
    
    # 调用Gemini API分析单词
    prompt = f"请详细分析以下英语单词：{word}"
    prompt += "\n请按照以下JSON格式返回结果："
    prompt += "{\"word\": \"单词\", \"phonetic\": \"音标\", \"translation\": \"中文释义\", \"examples\": [{\"sentence\": \"例句\", \"translation\": \"例句翻译\"}, ...]}"
    
    try:
        app_logger.info(f"调用Gemini API分析单词，单词: {word}")
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        # 缓存结果
        examples_json = json.dumps(result["examples"])
        vocab = Vocabulary(
            user_id=user_id,
            word=result["word"],
            phonetic=result["phonetic"],
            translation=result["translation"],
            examples=examples_json
        )
        db.add(vocab)
        db.commit()
        app_logger.info(f"单词分析完成并缓存，用户ID: {user_id}，单词: {word}")
        
        return WordAnalysis(**result)
    except Exception as e:
        app_logger.error(f"单词分析失败，单词: {word}，错误: {str(e)}")
        # 如果API调用失败，返回简单的默认格式
        return WordAnalysis(
            word=word,
            phonetic="",
            translation="查询失败",
            examples=[]
        )


def translate_sentence(sentence: str) -> SentenceTranslation:
    """翻译句子"""
    app_logger.info(f"翻译句子: {sentence[:50]}{'...' if len(sentence) > 50 else ''}")
    
    prompt = f"请将以下句子翻译成中文：{sentence}"
    prompt += "\n请仅返回翻译结果，不要添加任何额外信息。"
    
    try:
        app_logger.info(f"调用Gemini API翻译句子")
        response = model.generate_content(prompt)
        translation = response.text.strip()
        
        app_logger.info(f"句子翻译完成: {translation[:50]}{'...' if len(translation) > 50 else ''}")
        return SentenceTranslation(
            original=sentence,
            translation=translation
        )
    except Exception as e:
        app_logger.error(f"句子翻译失败，错误: {str(e)}")
        return SentenceTranslation(
            original=sentence,
            translation="翻译失败"
        )


def analyze_image(image_path: str) -> str:
    """分析图片内容"""
    try:
        # 读取图片文件
        with open(image_path, "rb") as file:
            image_data = file.read()
        
        # 创建图像对象
        image_parts = [
            {
                "mime_type": "image/jpeg" if image_path.endswith(".jpg") or image_path.endswith(".jpeg") else "image/png",
                "data": image_data
            }
        ]
        
        # 调用Gemini API分析图像
        prompt = "请识别并提取图片中的所有文本内容，以纯文本格式返回。"
        response = model.generate_content([prompt, image_parts[0]])
        
        return response.text
    except Exception as e:
        return f"图片分析失败: {str(e)}"


def analyze_document_content(content: str) -> dict:
    """分析文档内容，提取词汇和语法结构"""
    prompt = f"请分析以下文档内容，提取关键词汇和语法结构：\n{content[:5000]}"
    prompt += "\n请按照以下JSON格式返回结果："
    prompt += "{\"vocabulary\": [\"单词1\", \"单词2\", ...], \"grammar_points\": [\"语法点1\", \"语法点2\", ...]}"
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return result
    except Exception as e:
        return {
            "vocabulary": [],
            "grammar_points": []
        }