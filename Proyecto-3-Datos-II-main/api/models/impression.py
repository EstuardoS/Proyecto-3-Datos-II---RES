from pydantic import BaseModel
from typing import List, Dict

class AdDetails(BaseModel):
    advertiser: Dict
    campaign: Dict
    ad: Dict

class ImpressionEvent(BaseModel):
    impression_id: str
    user_ip: str
    user_agent: str
    timestamp: str
    state: str
    search_keywords: str
    session_id: str
    ads: List[AdDetails]
