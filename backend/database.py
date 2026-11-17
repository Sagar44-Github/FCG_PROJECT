"""Small SQLite persistence layer with explicit, parameterized queries."""
from __future__ import annotations
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from colour_engine.config import ROOT

DB_PATH = Path(os.getenv("Q3_DATABASE_PATH", str(ROOT / "data" / "q3.sqlite3")))

@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS render_jobs (
          id TEXT PRIMARY KEY, status TEXT NOT NULL, request_json TEXT NOT NULL,
          result_json TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS colour_comparisons (
          id TEXT PRIMARY KEY, colour_id TEXT NOT NULL, illumination_id TEXT NOT NULL,
          result_json TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS donation_simulations (
          id TEXT PRIMARY KEY, illumination_id TEXT NOT NULL, recognition TEXT NOT NULL,
          capacity_per_day INTEGER NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS analysis_jobs (
          id TEXT PRIMARY KEY, status TEXT NOT NULL, request_json TEXT NOT NULL,
          result_json TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_render_jobs_status_created ON render_jobs(status,created_at);
        CREATE INDEX IF NOT EXISTS idx_comparisons_illum_created ON colour_comparisons(illumination_id,created_at);
        CREATE INDEX IF NOT EXISTS idx_donations_illum_created ON donation_simulations(illumination_id,created_at);
        """)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def insert_render_job(job_id: str, request: dict) -> dict:
    now=now_iso()
    with connect() as db:
        db.execute("INSERT INTO render_jobs(id,status,request_json,created_at,updated_at) VALUES(?,?,?,?,?)",
                   (job_id,"queued",json.dumps(request),now,now))
    return get_render_job(job_id)

def update_render_job(job_id: str, status: str, result: dict | None = None, error: str | None = None) -> None:
    with connect() as db:
        db.execute("UPDATE render_jobs SET status=?,result_json=?,error=?,updated_at=? WHERE id=?",
                   (status,json.dumps(result) if result is not None else None,error,now_iso(),job_id))

def get_render_job(job_id: str) -> dict | None:
    with connect() as db: row=db.execute("SELECT * FROM render_jobs WHERE id=?",(job_id,)).fetchone()
    return _render_dict(row) if row else None

def list_render_jobs(limit: int, offset: int, status: str | None = None) -> tuple[list[dict], int]:
    where=" WHERE status=?" if status else ""; args=(status,) if status else ()
    with connect() as db:
        total=db.execute("SELECT count(*) FROM render_jobs"+where,args).fetchone()[0]
        rows=db.execute("SELECT * FROM render_jobs"+where+" ORDER BY created_at DESC LIMIT ? OFFSET ?",args+(limit,offset)).fetchall()
    return [_render_dict(r) for r in rows],total

def _render_dict(row) -> dict:
    return {"id":row["id"],"status":row["status"],"request":json.loads(row["request_json"]),
            "result":json.loads(row["result_json"]) if row["result_json"] else None,
            "error":row["error"],"created_at":row["created_at"],"updated_at":row["updated_at"]}

def insert_comparison(comparison_id: str, colour_id: str, illumination_id: str, result: dict) -> None:
    with connect() as db:
        db.execute("INSERT INTO colour_comparisons VALUES(?,?,?,?,?)",
                   (comparison_id,colour_id,illumination_id,json.dumps(result),now_iso()))

def get_comparison(comparison_id: str) -> dict | None:
    with connect() as db: row=db.execute("SELECT * FROM colour_comparisons WHERE id=?",(comparison_id,)).fetchone()
    if not row:return None
    return {"id":row["id"],"colour_id":row["colour_id"],"illumination_id":row["illumination_id"],
            "result":json.loads(row["result_json"]),"created_at":row["created_at"]}

def list_comparisons(limit: int, offset: int, illumination_id: str | None = None) -> tuple[list[dict],int]:
    where=" WHERE illumination_id=?" if illumination_id else ""; args=(illumination_id,) if illumination_id else ()
    with connect() as db:
        total=db.execute("SELECT count(*) FROM colour_comparisons"+where,args).fetchone()[0]
        rows=db.execute("SELECT * FROM colour_comparisons"+where+" ORDER BY created_at DESC LIMIT ? OFFSET ?",args+(limit,offset)).fetchall()
    return [{"id":r["id"],"colour_id":r["colour_id"],"illumination_id":r["illumination_id"],
             "result":json.loads(r["result_json"]),"created_at":r["created_at"]} for r in rows],total

def insert_donation(sim_id: str, illumination_id: str, recognition: str, capacity: int, result: dict) -> None:
    with connect() as db:
        db.execute("INSERT INTO donation_simulations VALUES(?,?,?,?,?,?)",
                   (sim_id,illumination_id,recognition,capacity,json.dumps(result),now_iso()))

def get_donation(sim_id: str) -> dict | None:
    with connect() as db: row=db.execute("SELECT * FROM donation_simulations WHERE id=?",(sim_id,)).fetchone()
    if not row:return None
    return {"id":row["id"],"illumination_id":row["illumination_id"],"recognition":row["recognition"],
            "capacity_per_day":row["capacity_per_day"],"result":json.loads(row["result_json"]),"created_at":row["created_at"]}

def list_donations(limit: int, offset: int, illumination_id: str | None = None,
                   recognition: str | None = None) -> tuple[list[dict],int]:
    clauses=[]; args=[]
    if illumination_id:clauses.append("illumination_id=?");args.append(illumination_id)
    if recognition:clauses.append("recognition=?");args.append(recognition)
    where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
    with connect() as db:
        total=db.execute("SELECT count(*) FROM donation_simulations"+where,args).fetchone()[0]
        rows=db.execute("SELECT * FROM donation_simulations"+where+" ORDER BY created_at DESC LIMIT ? OFFSET ?",tuple(args+[limit,offset])).fetchall()
    return [{"id":r["id"],"illumination_id":r["illumination_id"],"recognition":r["recognition"],
             "capacity_per_day":r["capacity_per_day"],"result":json.loads(r["result_json"]),"created_at":r["created_at"]} for r in rows],total

def insert_analysis_job(job_id: str, request: dict) -> dict:
    now=now_iso()
    with connect() as db:
        db.execute("INSERT INTO analysis_jobs(id,status,request_json,created_at,updated_at) VALUES(?,?,?,?,?)",
                   (job_id,"queued",json.dumps(request),now,now))
    return get_analysis_job(job_id)

def has_active_analysis_job() -> bool:
    with connect() as db:
        return db.execute("SELECT 1 FROM analysis_jobs WHERE status IN ('queued','running') LIMIT 1").fetchone() is not None

def update_analysis_job(job_id: str, status: str, result: dict | None = None, error: str | None = None) -> None:
    with connect() as db:
        db.execute("UPDATE analysis_jobs SET status=?,result_json=?,error=?,updated_at=? WHERE id=?",
                   (status,json.dumps(result) if result is not None else None,error,now_iso(),job_id))

def _analysis_dict(row) -> dict:
    return {"id":row["id"],"status":row["status"],"request":json.loads(row["request_json"]),
            "result":json.loads(row["result_json"]) if row["result_json"] else None,
            "error":row["error"],"created_at":row["created_at"],"updated_at":row["updated_at"]}

def get_analysis_job(job_id: str) -> dict | None:
    with connect() as db: row=db.execute("SELECT * FROM analysis_jobs WHERE id=?",(job_id,)).fetchone()
    return _analysis_dict(row) if row else None

def list_analysis_jobs(limit: int, offset: int, status: str | None = None) -> tuple[list[dict],int]:
    where=" WHERE status=?" if status else "";args=(status,) if status else ()
    with connect() as db:
        total=db.execute("SELECT count(*) FROM analysis_jobs"+where,args).fetchone()[0]
        rows=db.execute("SELECT * FROM analysis_jobs"+where+" ORDER BY created_at DESC LIMIT ? OFFSET ?",args+(limit,offset)).fetchall()
    return [_analysis_dict(row) for row in rows],total

