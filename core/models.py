"""
SQLAlchemy models for PostgreSQL database
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class File(Base):
    """File model for storing file information"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_name = Column(String(255), nullable=False, index=True)
    file_page = Column(Text)
    title = Column(Text)
    categories = Column(Text)
    language = Column(String(10), default="uz")
    description = Column(Text)
    file_url = Column(Text)
    image = Column(Text)
    year = Column(String(4))
    country = Column(String(255))
    actors = Column(Text)
    local_path = Column(Text)
    file_size = Column(BigInteger)
    mime = Column(String(255))
    telegram_type = Column(String(50))
    uploaded = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    uploaded_at = Column(DateTime)
    
    def __repr__(self):
        return f"<File(id={self.id}, title='{self.title}', config_name='{self.config_name}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'config_name': self.config_name,
            'file_page': self.file_page,
            'title': self.title,
            'categories': self.categories,
            'language': self.language,
            'description': self.description,
            'file_url': self.file_url,
            'image': self.image,
            'year': self.year,
            'country': self.country,
            'actors': self.actors,
            'local_path': self.local_path,
            'file_size': self.file_size,
            'mime': self.mime,
            'telegram_type': self.telegram_type,
            'uploaded': self.uploaded,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }