# Purpose: App startup tasks (create tables, create FTS if needed)
from sqlalchemy.ext.asyncio import AsyncEngine                                                # Async engine type
from sqlalchemy import text                                                                  # Raw SQL
from .database import engine, Base                                                           # Engine & Base
from .models_db import *                                                                     # Ensure models import

async def on_startup():
    """Create tables and FTS index if not exists."""
    async with engine.begin() as conn:
        # Create ORM tables
        await conn.run_sync(Base.metadata.create_all)
        # Create FTS5 virtual table for RAG (BM25), if not exists
        # We keep a separate FTS table synced by code for simplicity
        await conn.execute(
            text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS rag_docs_fts USING fts5(
                title, city, content, content='rag_docs', content_rowid='id'
            );
            """)
        )
        # Sync existing rows into FTS index (safe no-op on empty)
        await conn.execute(text("INSERT INTO rag_docs_fts(rag_docs_fts) VALUES('rebuild')"))
