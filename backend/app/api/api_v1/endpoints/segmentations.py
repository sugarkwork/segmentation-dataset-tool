from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_segmentations():
    return {"message": "Segmentations endpoint - TODO: implement"}