from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Boolean, String, Date, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import datetime

Base = declarative_base()
metadata = Base.metadata

def _get_datetime():
    return datetime.datetime.now()

class User(Base):
    __tablename__ = "user"

    ## common ##
    created_at = Column(DateTime, default=_get_datetime, nullable=False)
    updated_at = Column(
        DateTime, default=_get_datetime, onupdate=_get_datetime, nullable=False
    )
    id = Column(
        Integer, primary_key=True, index=True, nullable=False
    )
    ########################################################################################
    foreign_name = Column(String(length=255))
    age = Column(Integer)
    gender = Column(String(length=50))
    nationality = Column(String(length=100))
    passport_number = Column(String(length=50), unique=True)
    issuance_date = Column(Date)
    expiration_date = Column(Date)
    registration_number = Column(String(length=50))
    validity_period = Column(String(length=100))
    self_introduction = Column(String(length=500))

    experiences = relationship("Experience", back_populates="user")
    careers = relationship("Career", back_populates="user")


class Education(Base):
    __tablename__ = "education"

    ## common ##
    created_at = Column(DateTime, default=_get_datetime, nullable=False)
    updated_at = Column(
        DateTime, default=_get_datetime, onupdate=_get_datetime, nullable=False
    )
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    ########################################################################################
    school_name = Column(String(length=255))
    degree = Column(String(length=100))
    duration = Column(String(length=50))  # Format: YYYY (year-only) or YYYY-MM (year/month)
    major = Column(String(length=255))
    status = Column(String(length=50))
    # 시작일 = Column(String(length=50))  # Format: YYYY (year-only)
    # 종료일 = Column(String(length=50))  # Format: YYYY-MM (year/month)


class Experience(Base):
    __tablename__ = "experience"

    ## common ##
    created_at = Column(DateTime, default=_get_datetime, nullable=False)
    updated_at = Column(
        DateTime, default=_get_datetime, onupdate=_get_datetime, nullable=False
    )
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    ########################################################################################
    company_name = Column(String(length=255))
    job_title = Column(String(length=100))
    duration = Column(String(length=50))
