import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

from utils.logger_core import logger
from core.FileDB import FileDB


class AsyncDBWriter:
    """Asynchronous DB writer that consumes items from a queue and writes in batches.

    - Uses bulk upsert to minimize round-trips
    - Retries transient failures
    - Caches to disk on persistent failure
    - Logs queue size, batch times for observability
    """

    def __init__(
        self,
        db: FileDB,
        config_name: str,
        queue: "asyncio.Queue[Dict]",
        batch_size: int = 100,
        cache_path: str = "logs/db_cache.jsonl",
        batch_timeout: float = 5.0,
        max_retries: int = 3,
    ):
        self.db = db
        self.config_name = config_name
        self.queue = queue
        self.batch_size = batch_size
        self.cache_path = Path(cache_path)
        self.batch_timeout = batch_timeout
        self.max_retries = max_retries
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._processed = 0

        # Ensure cache directory exists
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def processed_count(self) -> int:
        return self._processed

    async def start(self):
        if self._task is None:
            self._running = True
            # Load cached items if present
            await self._load_cache_into_queue()
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
            self._task = None

    async def _run(self):
        buffer: List[Dict] = []
        last_log = time.time()
        while self._running or not self.queue.empty() or buffer:
            try:
                # Try to fill buffer up to batch_size with timeout
                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=self.batch_timeout)
                    buffer.append(item)
                except asyncio.TimeoutError:
                    # Timeout without new items
                    pass

                # Backpressure observability: log queue size periodically
                now = time.time()
                if now - last_log > 2.0:
                    # Use debug to avoid noisy zero logs; switch to info when active
                    qsize = self.queue.qsize()
                    bsize = len(buffer)
                    if qsize > 0 or bsize > 0:
                        logger.info(f"🧯 Queue size={qsize} buffer={bsize}")
                    else:
                        logger.debug("🧯 Writer idle (waiting for items)")
                    last_log = now

                # If buffer is ready or timed out with items, flush
                if len(buffer) >= self.batch_size or (buffer and not self._running and self.queue.empty()):
                    t0 = time.time()
                    await self._flush_buffer(buffer)
                    t1 = time.time()
                    logger.info(f"💾 Batch upserted {len(buffer)} rows in {(t1 - t0) * 1000:.1f} ms")
                    self._processed += len(buffer)
                    buffer.clear()
            except Exception as e:
                logger.error(f"❌ DB writer loop error: {e}")
                await asyncio.sleep(1)

    async def _flush_buffer(self, buffer: List[Dict]):
        if not buffer:
            return
        attempts = 0
        while attempts < self.max_retries:
            attempts += 1
            try:
                # Run blocking bulk_upsert in a thread to avoid blocking the event loop
                await asyncio.to_thread(self.db.bulk_upsert_files, self.config_name, buffer, self.batch_size)
                return
            except Exception as e:
                sleep_s = min(2 ** attempts, 5)
                logger.warning(f"🔄 DB upsert retry {attempts}/{self.max_retries} in {sleep_s}s: {e}")
                await asyncio.sleep(sleep_s)

        # Persistent failure: cache to disk for later recovery
        await self._cache_to_disk(buffer)

    async def _cache_to_disk(self, items: List[Dict]):
        try:
            with self.cache_path.open("a", encoding="utf-8") as f:
                for it in items:
                    f.write(json.dumps(it, ensure_ascii=False) + "\n")
            logger.error(f"🛟 Cached {len(items)} items to {self.cache_path}")
        except Exception as e:
            logger.error(f"💀 Failed to cache items: {e}")

    async def _load_cache_into_queue(self):
        if not self.cache_path.exists():
            return
        try:
            restored = 0
            lines: List[str] = self.cache_path.read_text(encoding="utf-8").splitlines()
            for line in lines:
                try:
                    item = json.loads(line)
                    await self.queue.put(item)
                    restored += 1
                except Exception:
                    continue
            # Truncate cache after loading
            self.cache_path.write_text("", encoding="utf-8")
            if restored:
                logger.info(f"♻️ Restored {restored} cached items into queue")
        except Exception as e:
            logger.error(f"❌ Failed to load cache: {e}")
