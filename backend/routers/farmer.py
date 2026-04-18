from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_farmers():
    return {"farmers": []}