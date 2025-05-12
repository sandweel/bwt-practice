from sqlalchemy.orm import Session
from models import User
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, first_name, last_name, gender, nationality, organization, position, dob, email, password):
    user = User(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        nationality=nationality,
        organization=organization,
        position=position,
        dob=datetime.strptime(dob, "%Y-%m-%d"),
        email=email,
        password=password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, first_name: str, last_name: str, organization: str, position: str):
    user = db.query(User).filter(User.id == user_id).first()
    user.first_name = first_name
    user.last_name = last_name
    user.organization = organization
    user.position = position
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user_id: int, hashed_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password = hashed_password
        db.commit()
