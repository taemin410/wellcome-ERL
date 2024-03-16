from sqlalchemy.orm import Session

def get_object_by_id(db: Session, model, object_id: int):
    return db.query(model).filter(model.id == object_id).first()

def get_objects(db: Session, model):
    return db.query(model).all()

def create_object(db: Session, model, object_data: dict):
    obj = model(**object_data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_object(db: Session, obj, object_data: dict):
    for key, value in object_data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

def delete_object(db: Session, obj):
    db.delete(obj)
    db.commit()
    return True