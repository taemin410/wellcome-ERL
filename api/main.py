from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User, Education, Experience
from query import (
    get_user_by_id,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_education_by_id,
    get_educations,
    create_education,
    update_education,
    delete_education,
    get_experience_by_id,
    get_experiences,
    create_experience,
    update_experience,
    delete_experience,
)

app = FastAPI()


# User Endpoints
@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=list[User])
def read_users(db: Session = Depends(get_db)):
    return get_users(db)

@app.post("/users", response_model=User)
def create_new_user(user_data: dict, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return user

@app.put("/users/{user_id}", response_model=User)
def update_existing_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user(db, user, user_data)
    return updated_user

@app.delete("/users/{user_id}")
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user)
    return {"message": "User deleted successfully"}

# Education Endpoints

@app.get("/educations/{education_id}", response_model=Education)
def read_education(education_id: int, db: Session = Depends(get_db)):
    education = get_education_by_id(db, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    return education

@app.get("/educations", response_model=list[Education])
def read_educations(db: Session = Depends(get_db)):
    return get_educations(db)

@app.post("/educations", response_model=Education)
def create_new_education(education_data: dict, db: Session = Depends(get_db)):
    education = create_education(db, education_data)
    return education

@app.put("/educations/{education_id}", response_model=Education)
def update_existing_education(education_id: int, education_data: dict, db: Session = Depends(get_db)):
    education = get_education_by_id(db, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    updated_education = update_education(db, education, education_data)
    return updated_education

@app.delete("/educations/{education_id}")
def delete_existing_education(education_id: int, db: Session = Depends(get_db)):
    education = get_education_by_id(db, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    delete_education(db, education)
    return {"message": "Education deleted successfully"}

# Experience Endpoints

@app.get("/experiences/{experience_id}", response_model=Experience)
def read_experience(experience_id: int, db: Session = Depends(get_db)):
    experience = get_experience_by_id(db, experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    return experience

@app.get("/experiences", response_model=list[Experience])
def read_experiences(db: Session = Depends(get_db)):
    return get_experiences(db)

@app.post("/experiences", response_model=Experience)
def create_new_experience(experience_data: dict, db: Session = Depends(get_db)):
    experience = create_experience(db, experience_data)
    return experience

@app.put("/experiences/{experience_id}", response_model=Experience)
def update_existing_experience(experience_id: int, experience_data: dict, db: Session = Depends(get_db)):
    experience = get_experience_by_id(db, experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    updated_experience = update_experience(db, experience, experience_data)
    return updated_experience
