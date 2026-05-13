from fastapi import APIRouter
from app.services.esp32_service import check_esp32

router = APIRouter()

@router.get("/status")
async def status():

    online = await check_esp32()

    return {
        "status": "online" if online else "offline"
    }