import json
import sys
import time
from pathlib import Path

import pandas as pd

from source.context import Context


def run(input_path, result_path, progress_path):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    frames = {name: pd.DataFrame(rows) for name, rows in payload.items()}

    class ReportingContext(Context):
        def execute4specific_date(self, date):
            progress = {"date": str(date), "completed": len(self.result_storage.solution_dict), "total": len(self.input_data.demand_dict)}
            temporary = Path(progress_path).with_suffix(".tmp")
            temporary.write_text(json.dumps(progress), encoding="utf-8")
            temporary.replace(progress_path)
            return super().execute4specific_date(date)

    started = time.perf_counter()
    context = ReportingContext(load_from_file=False, param_file_dict=frames)
    results = context.run()
    clean = {name: json.loads(frame.to_json(orient="records", date_format="iso")) for name, frame in results.items()}
    kpis = clean["kpiOut.csv"]
    demand = clean["demandOut.csv"]
    supply = clean["supplyOut.csv"]
    rolls = sum(row["原始纸卷使用个数"] for row in kpis)
    produced_length = sum(row["幅宽"] * row["供给数量"] for row in supply)
    requested = sum(row["需求数量"] for row in demand)
    unfulfilled = sum(row["未满足数量"] for row in demand)
    result = {
        "success": True, "runtime": round(time.perf_counter() - started, 3),
        "summary": {
            "rolls": rolls, "patterns": sum(row["切割方案数量"] for row in kpis),
            "utilization": round(100 * produced_length / (rolls * context.input_data.original_size), 2) if rolls else 0,
            "fulfillment": round(100 * (requested - unfulfilled) / requested, 2),
            "unfulfilled": unfulfilled, "days": len(kpis),
        },
        "results": clean,
    }
    Path(result_path).write_text(json.dumps(result, ensure_ascii=False, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    run(*sys.argv[1:])
