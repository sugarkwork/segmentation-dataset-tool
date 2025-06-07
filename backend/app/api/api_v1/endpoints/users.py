from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from ....core.deps import get_db, get_current_user
from ....schemas.user import User

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user