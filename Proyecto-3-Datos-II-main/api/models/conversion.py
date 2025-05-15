from pydantic import BaseModel
from typing import List, Dict

class Item(BaseModel):
    product_id: str
    quantity: int
    unit_price: float

class ConversionAttributes(BaseModel):
    order_id: str
    items: List[Item]

class ConversionPathStep(BaseModel):
    event_type: str
    timestamp: str

class AttributionInfo(BaseModel):
    time_to_convert: int
    attribution_model: str
    conversion_path: List[ConversionPathStep]

class UserInfo(BaseModel):
    user_ip: str
    state: str
    session_id: str

class ConversionEvent(BaseModel):       
    conversion_id: str
    click_id: str
    impression_id: str
    timestamp: str
    conversion_type: str
    conversion_value: float
    conversion_currency: str
    conversion_attributes: ConversionAttributes
    attribution_info: AttributionInfo
    user_info: UserInfo
