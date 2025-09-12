# Purpose: Manage local knowledge docs (add/search) and retrieval for orchestrator grounding
from fastapi import APIRouter, Depends, HTTPException                                         # API tools
from sqlalchemy.ext.asyncio import AsyncSession                                              # Session type
from sqlalchemy import insert, select, text                                                  # SQL helpers
from pydantic import BaseModel                                                               # Request models
from typing import List                                                                      # Typing
from .database import get_session                                                            # DB dep
from .models_db import RagDoc                                                                # ORM
from .settings import Settings                                                               # RAG toggle

router = APIRouter(prefix="/rag", tags=["rag"])                                              # Router

class RagDocIn(BaseModel):
    title: str                                                                               # Doc title
    city: str                                                                                # City tag
    content: str                                                                             # Plain text

class RagDocOut(BaseModel):
    id: int                                                                                  # ID
    title: str                                                                               # Title
    city: str                                                                                # City
    content: str                                                                             # Content

@router.post("/docs", response_model=RagDocOut)
async def add_doc(body: RagDocIn, session: AsyncSession = Depends(get_session)):
    """Insert a document and update the FTS index."""
    if not Settings().dict().get("RAG_ENABLED", "true").lower() == "true":
        raise HTTPException(status_code=400, detail="RAG is disabled")
    # Insert into main table
    q = insert(RagDoc).values(title=body.title, city=body.city, content=body.content).returning(RagDoc.id)
    res = await session.execute(q)
    doc_id = res.scalar_one()
    await session.commit()
    # Update FTS index with direct SQL
    await session.execute(text("INSERT INTO rag_docs_fts(rowid, title, city, content) VALUES (:id,:t,:c,:x)"),
                          {"id": doc_id, "t": body.title, "c": body.city, "x": body.content})
    await session.commit()
    return RagDocOut(id=doc_id, title=body.title, city=body.city, content=body.content)

@router.get("/search", response_model=List[RagDocOut])
async def search(q: str, city: str | None = None, limit: int = 5, session: AsyncSession = Depends(get_session)):
    """Full-text search over local docs using BM25 ranking."""
    if not Settings().dict().get("RAG_ENABLED", "true").lower() == "true":
        return []
    # Build FTS query with optional city filter
    where_city = " AND city MATCH :c" if city else ""
    sql = text(f"""
      SELECT d.id, d.title, d.city, d.content
      FROM rag_docs_fts f
      JOIN rag_docs d ON d.id = f.rowid
      WHERE f.rag_docs_fts MATCH :q {where_city}
      ORDER BY bm25(f) ASC
      LIMIT :lim
    """)
    params = {"q": q, "lim": limit}
    if city:
        params["c"] = city
    rows = (await session.execute(sql, params)).mappings().all()
    return [RagDocOut(**dict(r)) for r in rows]

async def retrieve_context(city: str, preferences: list[str], session: AsyncSession, limit: int = 5) -> str:
    """Helper used by orchestrator: pull top local docs as grounding context."""
    if not Settings().rag_enabled:
        raise HTTPException(status_code=400, detail="RAG is disabled")
    # Build a simple query string (city + preferences) to bias BM25
    q = " ".join([city] + preferences)
    rows = await search(q=q, city=city, limit=limit, session=session)
    # Concatenate small context (keep it short for LLM token budget)
    parts = [f"[{r.title}] {r.content[:500]}" for r in rows]  # Truncate each doc
    return "\n\n".join(parts)
