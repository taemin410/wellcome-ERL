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
    foreign_name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    nationality = Column(String)
    passport_number = Column(String, unique=True)
    issuance_date = Column(Date)
    expiration_date = Column(Date)
    registration_number = Column(String)
    validity_period = Column(String)
    self_introduction = Column(String)

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
    school_name = Column(String)
    degree = Column(String)
    duration = Column(String)  # Format: YYYY (year-only) or YYYY-MM (year/month)
    major = Column(String)
    status = Column(String)
    # 시작일 = Column(String)  # Format: YYYY (year-only)
    # 종료일 = Column(String)  # Format: YYYY-MM (year/month)

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
    company_name = Column(String)
    job_title = Column(String)
    duration = Column(String)
