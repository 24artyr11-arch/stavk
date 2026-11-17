from datetime import datetime, timezone
from pathlib import Path
import asyncio

import aiosqlite

from app.config import settings
from app.texts import clear_custom_text, load_custom_texts, set_custom_text


class Database:
    def __init__(self) -> None:
        self.conn: aiosqlite.Connection | None = None
        self.lock = asyncio.Lock()

    async def connect(self) -> None:
        path = Path(settings.database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL DEFAULT 'ru',
                registered INTEGER NOT NULL DEFAULT 0,
                deposited INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS referrals (
                click_id TEXT PRIMARY KEY,
                telegram_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS analyses_user_time_idx ON analyses(telegram_id, created_at);
            CREATE TABLE IF NOT EXISTS texts (
                language TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY(language, key)
            );
        """)
        await self.conn.commit()
        cur = await self.conn.execute("SELECT language,key,value FROM texts")
        rows = await cur.fetchall()
        load_custom_texts([dict(row) for row in rows])

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    def _connection(self) -> aiosqlite.Connection:
        if not self.conn:
            raise RuntimeError("Database is not connected")
        return self.conn

    async def ensure_user(self, telegram_id: int) -> None:
        async with self.lock:
            await self._connection().execute(
                "INSERT OR IGNORE INTO users(telegram_id) VALUES(?)", (telegram_id,)
            )
            await self._connection().commit()

    async def get_user(self, telegram_id: int):
        async with self.lock:
            cur = await self._connection().execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
            return await cur.fetchone()

    async def set_language(self, telegram_id: int, language: str) -> None:
        async with self.lock:
            await self._connection().execute("UPDATE users SET language=? WHERE telegram_id=?", (language, telegram_id))
            await self._connection().commit()

    async def create_referral(self, telegram_id: int) -> str:
        from uuid import uuid4
        click_id = uuid4().hex
        async with self.lock:
            await self._connection().execute(
                "INSERT INTO referrals(click_id,telegram_id) VALUES(?,?)", (click_id, telegram_id)
            )
            await self._connection().commit()
        return click_id

    async def get_setting(self, key: str) -> str | None:
        async with self.lock:
            cur = await self._connection().execute("SELECT value FROM settings WHERE key=?", (key,))
            row = await cur.fetchone()
            return row["value"] if row else None

    async def set_setting(self, key: str, value: str) -> None:
        async with self.lock:
            await self._connection().execute("""
                INSERT INTO settings(key,value) VALUES(?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, value))
            await self._connection().commit()

    async def get_text_rows(self) -> list[dict[str, str]]:
        async with self.lock:
            cur = await self._connection().execute("SELECT language,key,value FROM texts")
            return [dict(row) for row in await cur.fetchall()]

    async def set_text(self, language: str, key: str, value: str) -> None:
        async with self.lock:
            await self._connection().execute("""
                INSERT INTO texts(language,key,value) VALUES(?,?,?)
                ON CONFLICT(language,key) DO UPDATE SET value=excluded.value
            """, (language, key, value))
            await self._connection().commit()
        set_custom_text(language, key, value)

    async def clear_text(self, language: str, key: str) -> None:
        async with self.lock:
            await self._connection().execute(
                "DELETE FROM texts WHERE language=? AND key=?", (language, key)
            )
            await self._connection().commit()
        clear_custom_text(language, key)

    async def activate_event(self, click_id: str, event: str) -> tuple[int, bool] | None:
        event_l = event.strip().lower()
        is_deposit = any(x in event_l for x in ("firstdep", "first_deposit", "first deposit", "deposit", "dep"))
        is_registration = any(x in event_l for x in ("registration", "register", "signup", "reg"))
        if not (is_deposit or is_registration):
            return None
        async with self.lock:
            conn = self._connection()
            await conn.execute("BEGIN IMMEDIATE")
            try:
                cur = await conn.execute("""
                    SELECT u.telegram_id, u.registered, u.deposited
                    FROM referrals r JOIN users u USING (telegram_id)
                    WHERE r.click_id=?
                """, (click_id,))
                row = await cur.fetchone()
                if row is None:
                    await conn.rollback()
                    return None
                telegram_id = int(row["telegram_id"])
                if is_deposit:
                    await conn.execute("UPDATE users SET registered=1,deposited=1 WHERE telegram_id=?", (telegram_id,))
                    changed = not bool(row["deposited"])
                else:
                    await conn.execute("UPDATE users SET registered=1 WHERE telegram_id=?", (telegram_id,))
                    changed = not bool(row["registered"])
                await conn.commit()
                return telegram_id, changed
            except Exception:
                await conn.rollback()
                raise

    async def reserve_analysis(self, telegram_id: int, limit: int) -> tuple[bool, int, int | None]:
        async with self.lock:
            conn = self._connection()
            await conn.execute("BEGIN IMMEDIATE")
            try:
                cur = await conn.execute("SELECT deposited FROM users WHERE telegram_id=?", (telegram_id,))
                row = await cur.fetchone()
                if not row or not row["deposited"]:
                    await conn.rollback()
                    return False, 0, None
                cur = await conn.execute(
                    "SELECT COUNT(*) AS n FROM analyses WHERE telegram_id=? AND date(created_at)=date('now')",
                    (telegram_id,),
                )
                used = int((await cur.fetchone())["n"])
                if used >= limit:
                    await conn.rollback()
                    return False, used, None
                now = datetime.now(timezone.utc).isoformat()
                cur = await conn.execute(
                    "INSERT INTO analyses(telegram_id,created_at) VALUES(?,?)", (telegram_id, now)
                )
                analysis_id = int(cur.lastrowid)
                await conn.commit()
                return True, used + 1, analysis_id
            except Exception:
                await conn.rollback()
                raise

    async def get_analysis_usage(self, telegram_id: int) -> int:
        async with self.lock:
            cur = await self._connection().execute(
                "SELECT COUNT(*) AS n FROM analyses WHERE telegram_id=? AND date(created_at)=date('now')",
                (telegram_id,),
            )
            return int((await cur.fetchone())["n"])

    async def rollback_analysis(self, analysis_id: int) -> None:
        async with self.lock:
            await self._connection().execute("DELETE FROM analyses WHERE id=?", (analysis_id,))
            await self._connection().commit()


db = Database()

