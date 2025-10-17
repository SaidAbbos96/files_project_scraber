import sqlite3
from datetime import datetime
from core.config import DB_PATH


class FileDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # ✅ dict-style natija
        return conn

    def _init_db(self):
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_name TEXT,
            file_page TEXT,
            title TEXT,
            categories TEXT,
            language TEXT,
            description TEXT,
            file_url TEXT,
            image TEXT,
            year TEXT,
            country TEXT,
            actors TEXT,
            local_path TEXT,
            file_size INTEGER,
            mime TEXT,
            telegram_type TEXT,
            uploaded BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            uploaded_at TEXT
        )
        """
        )
        conn.commit()
        conn.close()

    # --- CRUD funksiyalar ---

    def get_files(self, config_name, sort_by_size=None):
        conn = self._connect()
        conn.row_factory = sqlite3.Row  # 🔑 Har bir natija Row obyekt bo'ladi
        c = conn.cursor()

        sql = "SELECT * FROM files WHERE config_name=?"
        if sort_by_size is not None:
            if sort_by_size == 1:
                sql += " ORDER BY file_size ASC"  # 1 = eng kichikdan boshla
            elif sort_by_size == 0:
                sql += " ORDER BY file_size DESC"  # 0 = eng kattadan boshla
            # boshqa qiymatlarda sort qilinmaydi

        c.execute(sql, (config_name,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]  # ✅ endi dict sifatida qaytaradi

    def get_file(self, file_id):
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM files WHERE id=?", (file_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None  # ✅ dict yoki None

    def insert_file(self, config_name, item):
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            """
        INSERT INTO files (
            config_name, file_page, title, categories, language, description,
            file_url, image, year, country, actors,
            local_path, file_size, mime, telegram_type, uploaded
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                config_name,
                item.get("file_page"),
                item.get("title"),
                item.get("categories"),
                item.get("language") or "uz",
                item.get("description"),
                item.get("file_url"),
                item.get("image"),
                item.get("year"),
                item.get("country"),
                item.get("actors"),
                item.get("local_path"),
                item.get("file_size"),
                item.get("mime"),
                item.get("telegram_type"),
                int(item.get("uploaded", False)),
            ),
        )
        conn.commit()
        conn.close()

    def update_file(self, file_id, **kwargs):
        if not kwargs:
            return

        conn = self._connect()
        c = conn.cursor()

        fields = []
        values = []

        for key, val in kwargs.items():
            if key == "uploaded" and val:
                fields.append("uploaded_at=?")
                values.append(datetime.utcnow().isoformat())
            fields.append(f"{key}=?")
            values.append(val)

        values.append(file_id)
        sql = f"UPDATE files SET {', '.join(fields)} WHERE id=?"
        c.execute(sql, tuple(values))
        conn.commit()
        conn.close()

    def delete_file(self, file_id):
        conn = self._connect()
        c = conn.cursor()
        c.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()
        conn.close()

    def delete_files(self, config_name):
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM files WHERE config_name=?", (config_name,))
        count = c.fetchone()[0]
        c.execute("DELETE FROM files WHERE config_name=?", (config_name,))
        conn.commit()
        conn.close()
        return count

    def file_exists(self, config_name: str, file_page: str) -> bool:
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "SELECT 1 FROM files WHERE config_name=? AND file_page=? LIMIT 1",
            (config_name, file_page),
        )
        exists = c.fetchone() is not None
        conn.close()
        return exists

    def get_files_count(self, config_name: str) -> int:
        """Bitta config'dagi jami fayllar sonini qaytarish"""
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM files WHERE config_name=?", (config_name,))
        count = c.fetchone()[0]
        conn.close()
        return count

    def get_downloaded_files_count(self, config_name: str) -> int:
        """Yuklangan fayllar sonini qaytarish (local_path mavjud)"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM files WHERE config_name=? AND local_path IS NOT NULL AND local_path != ''",
            (config_name,)
        )
        count = c.fetchone()[0]
        conn.close()
        return count

    def get_uploaded_files_count(self, config_name: str) -> int:
        """Telegramga yuklangan fayllar sonini qaytarish"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM files WHERE config_name=? AND uploaded=1",
            (config_name,)
        )
        count = c.fetchone()[0]
        conn.close()
        return count

    def reset_uploaded_status(self, config_name: str) -> int:
        """Bitta config'dagi barcha fayllarning uploaded statusini reset qilish
        
        Args:
            config_name: Config nomi
            
        Returns:
            int: Reset qilingan fayllar soni
        """
        conn = self._connect()
        c = conn.cursor()
        
        # Avval nechta fayl reset qilinishini sanash
        c.execute(
            "SELECT COUNT(*) FROM files WHERE config_name=? AND uploaded=1",
            (config_name,)
        )
        reset_count = c.fetchone()[0]
        
        # Uploaded statusni reset qilish
        c.execute(
            "UPDATE files SET uploaded=0, uploaded_at=NULL WHERE config_name=?",
            (config_name,)
        )
        
        conn.commit()
        conn.close()
        
        return reset_count
