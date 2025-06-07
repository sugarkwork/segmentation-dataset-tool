from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_annotations():
    return {"message": "Annotations endpoint - TODO: implement"}