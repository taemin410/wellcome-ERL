from sqlalchemy.orm import Session
from crud import get_object_by_id, get_objects, create_object, update_object, delete_object
from models import User, Education, Experience

def get_user_by_id(db: Session, user_id: int):
    return get_object_by_id(db, User, user_id)

def get_users(db: Session):
    return get_objects(db, User)

def create_user(db: Session, user_data: dict):
    return create_object(db, User, user_data)

def update_user(db: Session, user: User, user_data: dict):
    return update_object(db, user, user_data)

def delete_user(db: Session, user: User):
    return delete_object(db, user)

def get_education_by_id(db: Session, education_id: int):
    return get_object_by_id(db, Education, education_id)

def get_educations(db: Session):
    return get_objects(db, Education)

def create_education(db: Session, education_data: dict):
    return create_object(db, Education, education_data)

def update_education(db: Session, education: Education, education_data: dict):
    return update_object(db, education, education_data)

def delete_education(db: Session, education: Education):
    return delete_object(db, education)

def get_experience_by_id(db: Session, experience_id: int):
    return get_object_by_id(db, Experience, experience_id)

def get_experiences(db: Session):
    return get_objects(db, Experience)

def create_experience(db: Session, experience_data: dict):
    return create_object(db, Experience, experience_data)

def update_experience(db: Session, experience: Experience, experience_data: dict):
    return update_object(db, experience, experience_data)

def delete_experience(db: Session, experience: Experience):
    return delete_object(db, experience)
