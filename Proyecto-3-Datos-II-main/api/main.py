from fastapi import FastAPI
from pydantic import BaseModel
from queue_colas.producer import send_message  # Corrigiendo el import

app = FastAPI()

# Modelos Pydantic
class Impression(BaseModel):
    impression_id: str
    user_ip: str
    user_agent: str
    timestamp: str
    state: str
    search_keywords: str
    session_id: str
    ads: list

class Click(BaseModel):
    click_id: str
    impression_id: str
    timestamp: str
    clicked_ad: dict
    user_info: dict

class Conversion(BaseModel):
    conversion_id: str
    click_id: str
    impression_id: str
    timestamp: str
    conversion_type: str
    conversion_value: float
    conversion_currency: str
    conversion_attributes: dict
    attribution_info: dict
    user_info: dict

# Endpoints
@app.post("/api/events/impressions")  # <-- Ya corregido (s agregada)
async def create_impression(impression: Impression):
    send_message("impressions_queue", impression.dict())  # dict() corregido para pydantic v1
    return {"message": "Impression event sent to the queue."}

@app.post("/api/events/click")
async def create_click(click: Click):
    send_message("clicks_queue", click.dict())
    return {"message": "Click event sent to the queue."}

@app.post("/api/events/conversions")  # <-- Ya corregido (s agregada)
async def create_conversion(conversion: Conversion):
    send_message("conversions_queue", conversion.dict())
    return {"message": "Conversion event sent to the queue."}
