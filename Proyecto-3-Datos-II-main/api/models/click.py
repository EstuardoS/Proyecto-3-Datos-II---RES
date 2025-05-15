from pydantic import BaseModel
from typing import Dict

class ClickCoordinates(BaseModel):
    x: int
    y: int
    normalized_x: float
    normalized_y: float

class ClickedAd(BaseModel):
    ad_id: str
    ad_position: int
    click_coordinates: ClickCoordinates
    time_to_click: float

class UserInfo(BaseModel):
    user_ip: str
    state: str
    session_id: str

class ClickEvent(BaseModel):
    click_id: str
    impression_id: str
    timestamp: str
    clicked_ad: ClickedAd
    user_info: UserInfo
