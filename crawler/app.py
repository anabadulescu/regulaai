from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, HttpUrl
import uvicorn
import asyncio
from scan import run_scan
from rule_engine import load_rules, evaluate_rules
import json
from typing import List, Optional
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(
    title="RegulaAI Scanner",
    description="API for scanning websites for GDPR compliance",
    version="0.1.0"
)

# Prometheus metrics
scan_duration_seconds = Histogram('scan_duration_seconds', 'Scan duration in seconds')
violations_total = Counter('violations_total', 'Total violations by severity', ['severity'])
badge_requests_total = Counter('badge_requests_total', 'Total badge requests')

# Assign weights to severities
SEVERITY_WEIGHTS = {
    "critical": 50,
    "high": 30,
    "medium": 15,
    "low": 5
}

def get_rule_weight(severity: str) -> int:
    return SEVERITY_WEIGHTS.get(severity, 10)

class ScanRequest(BaseModel):
    url: HttpUrl
    persona: Optional[str] = None

class BatchScanRequest(BaseModel):
    scans: List[ScanRequest]

@app.post("/scan")
async def scan_endpoint(request: ScanRequest):
    try:
        with scan_duration_seconds.time():
            scan_result = await run_scan(str(request.url), persona_id=request.persona)
        rules = load_rules()
        violations = evaluate_rules(scan_result, rules)
        for v in violations:
            violations_total.labels(severity=v['severity']).inc()
        total_weight = sum(get_rule_weight(v['severity']) for v in violations)
        score = max(0, 100 - total_weight)
        response = scan_result.copy()
        response["score"] = score
        response["violations"] = violations
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_scan")
async def batch_scan_endpoint(request: BatchScanRequest):
    async def scan_and_serialize(scan_req: ScanRequest):
        try:
            with scan_duration_seconds.time():
                scan_result = await run_scan(str(scan_req.url), persona_id=scan_req.persona)
            rules = load_rules()
            violations = evaluate_rules(scan_result, rules)
            for v in violations:
                violations_total.labels(severity=v['severity']).inc()
            total_weight = sum(get_rule_weight(v['severity']) for v in violations)
            score = max(0, 100 - total_weight)
            response = scan_result.copy()
            response["score"] = score
            response["violations"] = violations
            return json.dumps(response)
        except Exception as e:
            return json.dumps({"url": str(scan_req.url), "error": str(e)})

    async def ndjson_stream():
        coros = [scan_and_serialize(scan_req) for scan_req in request.scans]
        for fut in asyncio.as_completed(coros):
            result = await fut
            yield result + "\n"

    return StreamingResponse(ndjson_stream(), media_type="application/x-ndjson")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Example badge endpoint for badge_requests_total
@app.get("/badge/{site_id}")
def badge(site_id: str):
    badge_requests_total.inc()
    # ... badge generation logic ...
    return Response("<svg><!-- badge --></svg>", media_type="image/svg+xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 