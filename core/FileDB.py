"""
PostgreSQL-based FileDB implementation using SQLAlchemy
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from sqlalchemy import create_engine, func, desc, asc, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
import time

from core.config import get_database_url, get_db_engine_options
from core.models import File, Base

logger = logging.getLogger(__name__)


# Module-level engine/session to reuse connections across instances
_GLOBAL_ENGINE = None
_GLOBAL_SESSIONMAKER = None


class PostgreSQLFileDB:
    """PostgreSQL-based file database using SQLAlchemy"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize PostgreSQL database connection
        
        Args:
            database_url: PostgreSQL connection URL. If None, uses config
        """
        self.database_url = database_url or get_database_url()

        global _GLOBAL_ENGINE, _GLOBAL_SESSIONMAKER
        if _GLOBAL_ENGINE is None:
            engine_opts = get_db_engine_options()
            _GLOBAL_ENGINE = create_engine(self.database_url, **engine_opts)
            _GLOBAL_SESSIONMAKER = sessionmaker(bind=_GLOBAL_ENGINE)

        # Reuse the global engine/sessionmaker to avoid re-connecting per instance
        self.engine = _GLOBAL_ENGINE
        self.SessionLocal = _GLOBAL_SESSIONMAKER
    
    def _init_db(self):
        """Initialize database tables (disabled - use Alembic migrations)"""
        # Intentionally no-op to avoid expensive DDL checks on every startup
        return
    
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
            ins = pg_insert(File).values(
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
                uploaded=bool(item.get("uploaded", False)),
                created_at=func.now(),
            )

            # Upsert on unique (config_name, file_page) to avoid extra round-trips
            stmt = ins.on_conflict_do_update(
                index_elements=["config_name", "file_page"],  # type: ignore
                set_={
                    "title": ins.excluded.title,  # type: ignore
                    "categories": ins.excluded.categories,  # type: ignore
                    "language": ins.excluded.language,  # type: ignore
                    "description": ins.excluded.description,  # type: ignore
                    "file_url": ins.excluded.file_url,  # type: ignore
                    "image": ins.excluded.image,  # type: ignore
                    "year": ins.excluded.year,  # type: ignore
                    "country": ins.excluded.country,  # type: ignore
                    "actors": ins.excluded.actors,  # type: ignore
                    "local_path": ins.excluded.local_path,  # type: ignore
                    "file_size": ins.excluded.file_size,  # type: ignore
                    "mime": ins.excluded.mime,  # type: ignore
                    "telegram_type": ins.excluded.telegram_type,  # type: ignore
                    "uploaded": ins.excluded.uploaded,  # type: ignore
                },
            )

            result = session.execute(stmt.returning(File.id))
            session.commit()
            inserted_id = result.scalar()  # may be None if conflict
            return int(inserted_id) if inserted_id is not None else 0

    def bulk_upsert_files(self, config_name: str, items: List[Dict[str, Any]], batch_size: int = 500) -> int:
        """Bulk upsert multiple files using single transaction batches.

        Args:
            config_name: Configuration name
            items: List of file dicts
            batch_size: Number of rows per batch

        Returns:
            Number of rows attempted (inserted/updated)
        """
        if not items:
            return 0

        total = 0
        with self._get_session() as session:
            for i in range(0, len(items), batch_size):
                chunk = items[i:i + batch_size]
                t0 = time.time()
                values = []
                for item in chunk:
                    values.append({
                        "config_name": config_name,
                        "file_page": item.get("file_page"),
                        "title": item.get("title"),
                        "categories": item.get("categories"),
                        "language": item.get("language", "uz"),
                        "description": item.get("description"),
                        "file_url": item.get("file_url"),
                        "image": item.get("image"),
                        "year": item.get("year"),
                        "country": item.get("country"),
                        "actors": item.get("actors"),
                        "local_path": item.get("local_path"),
                        "file_size": item.get("file_size"),
                        "mime": item.get("mime"),
                        "telegram_type": item.get("telegram_type"),
                        "uploaded": bool(item.get("uploaded", False)),
                        "created_at": func.now(),
                    })

                ins = pg_insert(File).values(values)
                stmt = ins.on_conflict_do_update(
                    index_elements=["config_name", "file_page"],  # type: ignore
                    set_={
                        "title": ins.excluded.title,  # type: ignore
                        "categories": ins.excluded.categories,  # type: ignore
                        "language": ins.excluded.language,  # type: ignore
                        "description": ins.excluded.description,  # type: ignore
                        "file_url": ins.excluded.file_url,  # type: ignore
                        "image": ins.excluded.image,  # type: ignore
                        "year": ins.excluded.year,  # type: ignore
                        "country": ins.excluded.country,  # type: ignore
                        "actors": ins.excluded.actors,  # type: ignore
                        "local_path": ins.excluded.local_path,  # type: ignore
                        "file_size": ins.excluded.file_size,  # type: ignore
                        "mime": ins.excluded.mime,  # type: ignore
                        "telegram_type": ins.excluded.telegram_type,  # type: ignore
                        "uploaded": ins.excluded.uploaded,  # type: ignore
                    },
                )

                # Simple transient retry/backoff for operational errors
                attempts = 0
                while True:
                    try:
                        session.execute(stmt)
                        session.commit()
                        break
                    except OperationalError as e:
                        attempts += 1
                        if attempts >= 3:
                            logger.error(f"Bulk upsert failed after retries: {e}")
                            raise
                        sleep_s = min(2 ** attempts, 5)
                        logger.warning(f"Transient DB error, retrying in {sleep_s}s (attempt {attempts})")
                        time.sleep(sleep_s)
                total += len(chunk)
                t1 = time.time()
                logger.debug(f"Bulk upsert batch size={len(chunk)} elapsed_ms={(t1-t0)*1000:.1f}")

        return total
    
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

    def get_undownloaded_files_paginated(self, config_name: str, last_id: Optional[int], limit: int) -> List[Dict[str, Any]]:
        """Paginated fetch of undownloaded files ordered by id.

        Args:
            config_name: Configuration name
            last_id: Last processed id; fetch rows with id > last_id
            limit: Maximum number of files to return

        Returns:
            List of undownloaded files in ascending id order
        """
        with self._get_session() as session:
            query = session.query(File).filter(
                File.config_name == config_name,
                (File.uploaded.is_(None) | (File.uploaded == False)),
                (File.local_path.is_(None) | (File.local_path == '')),
                File.file_url.isnot(None),
                File.file_url != '',
                ~File.file_url.like('%t.me%')
            )
            if last_id is not None:
                query = query.filter(File.id > last_id)
            query = query.order_by(asc(File.id)).limit(limit)
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
            # Leverage unique index for fast existence check
            return session.query(File.id).filter(
                File.config_name == config_name,
                File.file_page == file_page
            ).limit(1).scalar() is not None

    def get_existing_pages(self, config_name: str, pages: List[str]) -> Set[str]:
        """Return a set of file_page values that already exist for the config.

        Args:
            config_name: Configuration name
            pages: List of file_page URLs to check

        Returns:
            Set of pages that exist in DB
        """
        if not pages:
            return set()

        t0 = time.time()
        with self._get_session() as session:
            rows = session.query(File.file_page).filter(
                File.config_name == config_name,
                File.file_page.in_(pages)
            ).all()
            existing = {r[0] for r in rows if r[0]}
            t1 = time.time()
            logger.debug(f"Existing check pages={len(pages)} found={len(existing)} elapsed_ms={(t1-t0)*1000:.1f}")
            return existing
    
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

    def get_download_statistics(self, config_name: str) -> Dict[str, Any]:
        """Compute download statistics using DB-side counts and sums.

        Returns keys: total_files, downloaded, pending, no_url, download_rate,
        total_size_gb, downloaded_size_gb, pending_size_gb
        """
        with self._get_session() as session:
            total_files = session.query(func.count(File.id)).filter(
                File.config_name == config_name
            ).scalar() or 0

            downloaded = session.query(func.count(File.id)).filter(
                File.config_name == config_name,
                File.local_path.isnot(None),
                File.local_path != ''
            ).scalar() or 0

            pending = session.query(func.count(File.id)).filter(
                File.config_name == config_name,
                (File.local_path.is_(None) | (File.local_path == '')),
                File.file_url.isnot(None),
                File.file_url != ''
            ).scalar() or 0

            no_url = session.query(func.count(File.id)).filter(
                File.config_name == config_name,
                (File.file_url.is_(None) | (File.file_url == ''))
            ).scalar() or 0

            total_size = session.query(func.sum(File.file_size)).filter(
                File.config_name == config_name,
                File.file_size.isnot(None)
            ).scalar() or 0

            downloaded_size = session.query(func.sum(File.file_size)).filter(
                File.config_name == config_name,
                File.local_path.isnot(None),
                File.local_path != '',
                File.file_size.isnot(None)
            ).scalar() or 0

            pending_size = (total_size - downloaded_size) if total_size and downloaded_size is not None else 0

            return {
                "total_files": int(total_files),
                "downloaded": int(downloaded),
                "pending": int(pending),
                "no_url": int(no_url),
                "download_rate": (float(downloaded) / float(total_files) * 100.0) if total_files else 0.0,
                "total_size_gb": float(total_size) / (1024 ** 3),
                "downloaded_size_gb": float(downloaded_size) / (1024 ** 3),
                "pending_size_gb": float(pending_size) / (1024 ** 3),
            }
    
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