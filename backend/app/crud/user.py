from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from ..core.security import get_password_hash, verify_password
from ..crud.base import CRUDBase
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_github_id(self, db: Session, *, github_id: str) -> Optional[User]:
        """Get user by GitHub ID"""
        return db.query(User).filter(User.github_id == github_id).first()

    def get_by_twitter_id(self, db: Session, *, twitter_id: str) -> Optional[User]:
        """Get user by Twitter ID"""
        return db.query(User).filter(User.twitter_id == twitter_id).first()

    def get_by_id(self, db: Session, *, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create user with hashed password"""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            theme=obj_in.theme,
            language=obj_in.language,
            oauth_provider="local"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_oauth_user(
        self, db: Session, *, user_data: Dict[str, Any]
    ) -> User:
        """Create user from OAuth provider"""
        db_obj = User(**user_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user, handling password hashing"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """Authenticate user by username/email and password"""
        # Try to find user by username or email
        user = self.get_by_username(db, username=username)
        if not user:
            user = self.get_by_email(db, email=username)
        
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.is_superuser

    def activate(self, db: Session, *, user: User) -> User:
        """Activate user"""
        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, *, user: User) -> User:
        """Deactivate user"""
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

# Create instance
user = CRUDUser(User)