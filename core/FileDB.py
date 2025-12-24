"""
PostgreSQL-based FileDB implementation using SQLAlchemy
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, func, desc, asc, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from core.config import get_database_url
from core.models import File, Base

logger = logging.getLogger(__name__)


class PostgreSQLFileDB:
    """PostgreSQL-based file database using SQLAlchemy"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize PostgreSQL database connection
        
        Args:
            database_url: PostgreSQL connection URL. If None, uses config
        """
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections every hour
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def _get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def get_files(self, config_name: str, sort_by_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all files for a config with optional sorting
        
        Args:
            config_name: Configuration name
            sort_by_size: 1 for ASC, 0 for DESC, None for no sorting
            
        Returns:
            List of file dictionaries
        """
        with self._get_session() as session:
            query = session.query(File).filter(File.config_name == config_name)
            
            if sort_by_size is not None:
                if sort_by_size == 1:
                    query = query.order_by(asc(File.file_size))
                elif sort_by_size == 0:
                    query = query.order_by(desc(File.file_size))
            
            files = query.all()
            return [file.to_dict() for file in files]
    
    def get_file(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get single file by ID
        
        Args:
            file_id: File ID
            
        Returns:
            File dictionary or None if not found
        """
        with self._get_session() as session:
            file = session.query(File).filter(File.id == file_id).first()
            return file.to_dict() if file else None
    
    def insert_file(self, config_name: str, item: Dict[str, Any]) -> int:
        """Insert new file
        
        Args:
            config_name: Configuration name
            item: File data dictionary
            
        Returns:
            ID of inserted file
        """
        with self._get_session() as session:
            file = File(
                config_name=config_name,
                file_page=item.get("file_page"),
                title=item.get("title"),
                categories=item.get("categories"),
                language=item.get("language", "uz"),
                description=item.get("description"),
                file_url=item.get("file_url"),
                image=item.get("image"),
                year=item.get("year"),
                country=item.get("country"),
                actors=item.get("actors"),
                local_path=item.get("local_path"),
                file_size=item.get("file_size"),
                mime=item.get("mime"),
                telegram_type=item.get("telegram_type"),
                uploaded=bool(item.get("uploaded", False))
            )
            session.add(file)
            session.commit()
            return file.id
    
    def update_file(self, file_id: int, **kwargs) -> bool:
        """Update file by ID
        
        Args:
            file_id: File ID
            **kwargs: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        if not kwargs:
            return False
            
        with self._get_session() as session:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False
            
            # Handle uploaded_at timestamp
            if kwargs.get("uploaded"):
                kwargs["uploaded_at"] = datetime.utcnow()
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(file, key):
                    setattr(file, key, value)
            
            session.commit()
            return True
    
    def delete_file(self, file_id: int) -> bool:
        """Delete file by ID
        
        Args:
            file_id: File ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._get_session() as session:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False
            
            session.delete(file)
            session.commit()
            return True
    
    def delete_files(self, config_name: str) -> int:
        """Delete all files for a config
        
        Args:
            config_name: Configuration name
            
        Returns:
            Number of deleted files
        """
        with self._get_session() as session:
            count = session.query(File).filter(File.config_name == config_name).count()
            session.query(File).filter(File.config_name == config_name).delete()
            session.commit()
            return count
    
    def get_undownloaded_files(self, config_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get files that haven't been downloaded
        
        Args:
            config_name: Configuration name
            limit: Maximum number of files to return
            
        Returns:
            List of undownloaded files
        """
        with self._get_session() as session:
            query = session.query(File).filter(
                File.config_name == config_name,
                (File.uploaded.is_(None) | (File.uploaded == False)),
                (File.local_path.is_(None) | (File.local_path == '')),
                File.file_url.isnot(None),
                File.file_url != '',
                ~File.file_url.like('%t.me%')
            ).order_by(File.id)
            
            if limit:
                query = query.limit(limit)
            
            files = query.all()
            return [file.to_dict() for file in files]
    
    def file_exists(self, config_name: str, file_page: str) -> bool:
        """Check if file exists
        
        Args:
            config_name: Configuration name
            file_page: File page URL
            
        Returns:
            True if exists, False otherwise
        """
        with self._get_session() as session:
            exists = session.query(
                session.query(File).filter(
                    File.config_name == config_name,
                    File.file_page == file_page
                ).exists()
            ).scalar()
            return exists
    
    def get_files_count(self, config_name: str) -> int:
        """Get total files count for config
        
        Args:
            config_name: Configuration name
            
        Returns:
            Total files count
        """
        with self._get_session() as session:
            return session.query(File).filter(File.config_name == config_name).count()
    
    def get_downloaded_files_count(self, config_name: str) -> int:
        """Get downloaded files count
        
        Args:
            config_name: Configuration name
            
        Returns:
            Downloaded files count
        """
        with self._get_session() as session:
            return session.query(File).filter(
                File.config_name == config_name,
                File.local_path.isnot(None),
                File.local_path != ''
            ).count()
    
    def get_uploaded_files_count(self, config_name: str) -> int:
        """Get uploaded files count
        
        Args:
            config_name: Configuration name
            
        Returns:
            Uploaded files count
        """
        with self._get_session() as session:
            return session.query(File).filter(
                File.config_name == config_name,
                File.uploaded == True
            ).count()
    
    def reset_uploaded_status(self, config_name: str) -> int:
        """Reset uploaded status for all files in config
        
        Args:
            config_name: Configuration name
            
        Returns:
            Number of reset files
        """
        with self._get_session() as session:
            # Count files to reset
            count = session.query(File).filter(
                File.config_name == config_name,
                File.uploaded == True
            ).count()
            
            # Reset uploaded status
            session.query(File).filter(
                File.config_name == config_name,
                File.uploaded == True
            ).update({
                File.uploaded: False,
                File.uploaded_at: None
            })
            
            session.commit()
            return count
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'engine'):
            self.engine.dispose()


# Create a global instance for backward compatibility
FileDB = PostgreSQLFileDB