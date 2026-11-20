import json
import logging
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = os.getenv("APP_BASE_PATH", "").rstrip("/")
app = FastAPI(title="Column Studio · 切割优化 API", root_path=BASE_PATH)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[value.strip() for value in os.getenv("ALLOWED_ORIGINS", "http://localhost:8091,http://127.0.0.1:8091").split(",") if value.strip()],
    allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
)
executor = ThreadPoolExecutor(max_workers=1)
jobs = {}
lock = threading.Lock()


class RunInput(BaseModel):
    demand: list[dict] = Field(min_length=1, max_length=2000)
    parameters: list[dict] = Field(min_length=2, max_length=8)


def number(value, label, minimum, maximum, integer=False):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise HTTPException(422, f"{label} 必须是数值")
    if not math.isfinite(parsed) or not minimum <= parsed <= maximum or (integer and not parsed.is_integer()):
        raise HTTPException(422, f"{label} 超出允许范围 {minimum}–{maximum}")
    return int(parsed) if integer else parsed


def validate_payload(payload):
    params = {}
    for row in payload.parameters:
        name = row.get("参数名")
        if not isinstance(name, str) or name in params:
            raise HTTPException(422, "参数名称缺失或重复")
        params[name] = row.get("参数值")
    limits = {
        "原始卷纸长度": (1, 100000, False), "最大切割次数": (1, 12, True),
        "余量下限": (0, 100000, False), "边损下限": (-1000, 0, False),
        "边损上限": (0, 100000, False), "切割方案使用下限": (0, 1000, True),
    }
    defaults = {"是否考虑边损": "否", "是否进行补库": "否", "余量下限": 1500, "边损下限": 0, "边损上限": 50}
    if "原始卷纸长度" not in params or "最大切割次数" not in params:
        raise HTTPException(422, "缺少原始卷纸长度或最大切割次数")
    params = {**defaults, **params}
    for name, value in list(params.items()):
        if name in limits:
            params[name] = number(value, name, *limits[name])
        elif name in ("是否考虑边损", "是否进行补库"):
            if value not in ("是", "否"):
                raise HTTPException(422, f"{name} 必须为是或否")
        else:
            raise HTTPException(422, f"未知参数：{name}")
    if params["余量下限"] > params["原始卷纸长度"] or params["边损上限"] > params["余量下限"]:
        raise HTTPException(422, "请满足：边损上限 ≤ 余量下限 ≤ 原始幅宽")
    demand = []
    dates = set()
    sizes = set()
    for row in payload.demand:
        try:
            date = pd.to_datetime(str(row.get("移库日期", "")), errors="raise").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            raise HTTPException(422, "移库日期无效，请使用 YYYY-MM-DD")
        width = number(row.get("幅宽"), "幅宽", 1, params["原始卷纸长度"])
        amount = number(row.get("订单件数"), "订单件数", 1, 100000, True)
        demand.append({"移库日期": date, "幅宽": width, "订单件数": amount})
        dates.add(date)
        sizes.add(width)
    if len(dates) > 14 or len(sizes) > 100:
        raise HTTPException(422, "单次最多 14 天、100 种幅宽")
    return {"demand.csv": demand, "global_params.csv": [{"参数名": name, "参数值": str(value)} for name, value in params.items()]}


def execute(job_id, payload):
    with tempfile.TemporaryDirectory(prefix="column-job-") as directory:
        folder = Path(directory)
        input_path, output_path, progress_path = [folder / name for name in ("input.json", "result.json", "progress.json")]
        input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        with lock:
            jobs[job_id].update(status="running", started=time.time(), progress_path=progress_path)
        try:
            with (folder / "solver.log").open("w", encoding="utf-8") as log:
                subprocess.run([sys.executable, "-m", "api.worker", str(input_path), str(output_path), str(progress_path)], cwd=ROOT, stdout=log, stderr=log, timeout=300, check=True)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            with lock:
                jobs[job_id].update(status="succeeded", result=result)
        except subprocess.TimeoutExpired:
            with lock:
                jobs[job_id].update(status="failed", error="求解超过 300 秒，请缩小数据规模后重试。")
        except Exception:
            logging.exception("Optimization job %s failed", job_id)
            logging.error("Solver log: %s", (folder / "solver.log").read_text(encoding="utf-8", errors="replace")[-6000:])
            with lock:
                jobs[job_id].update(status="failed", error="算法未能返回可用解，请检查幅宽、切割次数及边损约束。")
        finally:
            with lock:
                jobs[job_id].pop("progress_path", None)


@app.get("/api/health")
def health():
    return {"status": "ok", "solver": "glpk", "solver_available": shutil.which("glpsol") is not None}


@app.get("/api/example")
def example():
    return {"demand": json.loads(pd.read_csv(ROOT / "data/demand.csv").to_json(orient="records")), "parameters": json.loads(pd.read_csv(ROOT / "data/global_params.csv", dtype=str).to_json(orient="records"))}


@app.post("/api/jobs", status_code=202)
def create_job(payload: RunInput):
    validated = validate_payload(payload)
    if shutil.which("glpsol") is None:
        raise HTTPException(503, "GLPK 求解器未安装")
    with lock:
        if sum(job["status"] in ("queued", "running") for job in jobs.values()) >= 3:
            raise HTTPException(429, "任务队列已满，请稍后重试")
        while len(jobs) >= 20:
            expired = next((key for key, value in jobs.items() if value["status"] in ("succeeded", "failed")), None)
            if expired is None:
                break
            del jobs[expired]
        job_id = uuid.uuid4().hex
        jobs[job_id] = {"id": job_id, "status": "queued", "created": time.time()}
    executor.submit(execute, job_id, validated)
    return {"id": job_id, "status": "queued"}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    with lock:
        if job_id not in jobs:
            raise HTTPException(404, "任务不存在或已过期，请重新运行")
        job = dict(jobs[job_id])
        progress_path = job.pop("progress_path", None)
        if progress_path and progress_path.exists():
            job["progress"] = json.loads(progress_path.read_text(encoding="utf-8"))
    return job


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(f"{BASE_PATH}/studio/")


app.mount("/studio", StaticFiles(directory=ROOT / "frontend", html=True), name="studio")
