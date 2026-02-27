from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PaymentOrder(BaseModel):
    """支付订单响应模型"""
    order_id: str
    prepay_id: str
    timestamp: str
    nonce_str: str
    sign: str
    payment_params: dict
    
    class Config:
        orm_mode = True

class PaymentNotify(BaseModel):
    """支付通知模型"""
    appid: str
    mch_id: str
    nonce_str: str
    sign: str
    result_code: str
    return_code: str
    openid: str
    is_subscribe: str
    trade_type: str
    bank_type: str
    total_fee: int
    fee_type: str
    transaction_id: str
    out_trade_no: str
    time_end: str
    
    class Config:
        orm_mode = True