import time
import random
import hashlib
import requests
from sqlalchemy.orm import Session
from models import User
from schemas.payment import PaymentOrder
from config import settings
from datetime import datetime, timedelta


def create_subscription_order(db: Session, openid: str) -> PaymentOrder:
    """创建微信支付订阅订单"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise ValueError("用户不存在")
    
    # 生成订单号
    order_id = f"sub_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # 构建统一支付接口参数
    params = {
        "appid": settings.WX_APPID,
        "mch_id": settings.WX_MCH_ID,
        "nonce_str": generate_nonce_str(),
        "body": "语言学习小程序月卡订阅",
        "out_trade_no": order_id,
        "total_fee": settings.SUBSCRIPTION_PRICE,
        "spbill_create_ip": "127.0.0.1",
        "notify_url": settings.WX_NOTIFY_URL,
        "trade_type": "JSAPI",
        "openid": openid
    }
    
    # 生成签名
    params["sign"] = generate_sign(params)
    
    # 发送请求到微信支付接口
    xml_params = dict_to_xml(params)
    response = requests.post(
        "https://api.mch.weixin.qq.com/pay/unifiedorder",
        data=xml_params.encode("utf-8"),
        headers={"Content-Type": "text/xml"}
    )
    
    # 解析微信支付返回的XML
    response_dict = xml_to_dict(response.text)
    
    if response_dict.get("return_code") != "SUCCESS" or response_dict.get("result_code") != "SUCCESS":
        raise ValueError(f"微信支付下单失败: {response_dict.get('return_msg')}")
    
    prepay_id = response_dict.get("prepay_id")
    
    # 生成小程序端支付参数
    pay_sign_params = {
        "appId": settings.WX_APPID,
        "timeStamp": str(int(time.time())),
        "nonceStr": generate_nonce_str(),
        "package": f"prepay_id={prepay_id}",
        "signType": "MD5"
    }
    
    # 生成支付签名
    pay_sign_params["paySign"] = generate_sign(pay_sign_params)
    
    return PaymentOrder(
        order_id=order_id,
        prepay_id=prepay_id,
        timestamp=pay_sign_params["timeStamp"],
        nonce_str=pay_sign_params["nonceStr"],
        sign=pay_sign_params["paySign"],
        payment_params=pay_sign_params
    )


def handle_payment_notify(db: Session, notify_data: dict) -> bool:
    """处理微信支付回调通知"""
    # 验证签名
    if not verify_sign(notify_data):
        return False
    
    if notify_data.get("return_code") != "SUCCESS" or notify_data.get("result_code") != "SUCCESS":
        return False
    
    # 获取订单信息
    out_trade_no = notify_data.get("out_trade_no")
    openid = notify_data.get("openid")
    total_fee = int(notify_data.get("total_fee"))
    
    # 验证订单金额
    if total_fee != settings.SUBSCRIPTION_PRICE:
        return False
    
    # 更新用户订阅状态
    user = db.query(User).filter(User.openid == openid).first()
    if user:
        # 计算新的订阅到期时间
        if user.subscription_expiry and user.subscription_expiry > datetime.utcnow():
            # 如果当前订阅未过期，从当前过期时间开始延长
            new_expiry = user.subscription_expiry + timedelta(days=settings.SUBSCRIPTION_DURATION)
        else:
            # 如果当前订阅已过期，从当前时间开始计算
            new_expiry = datetime.utcnow() + timedelta(days=settings.SUBSCRIPTION_DURATION)
        
        user.subscription_expiry = new_expiry
        db.commit()
    
    return True


def generate_nonce_str(length: int = 32) -> str:
    """生成随机字符串"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for _ in range(length))


def generate_sign(params: dict) -> str:
    """生成签名"""
    # 按字典序排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    # 拼接字符串
    sign_str = "&amp;".join([f"{k}={v}" for k, v in sorted_params if v])
    # 添加API密钥
    sign_str += f"&amp;key={settings.WX_API_KEY}"
    # MD5加密
    md5 = hashlib.md5()
    md5.update(sign_str.encode("utf-8"))
    return md5.hexdigest().upper()


def verify_sign(params: dict) -> bool:
    """验证签名"""
    sign = params.pop("sign", "")
    generated_sign = generate_sign(params)
    return sign == generated_sign


def dict_to_xml(params: dict) -> str:
    """将字典转换为XML"""
    xml = ["<xml>"]
    for k, v in params.items():
        xml.append(f"<{k}>{v}</{k}>")
    xml.append("</xml>")
    return "".join(xml)


def xml_to_dict(xml_str: str) -> dict:
    """将XML转换为字典"""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_str)
    return {child.tag: child.text for child in root}