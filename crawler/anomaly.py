import os
import hashlib
from sqlalchemy import create_engine, text
from collections import Counter

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/regulaai")
engine = create_engine(DATABASE_URL)

def flag_script_anomalies(domain, script_hashes):
    # Get all historic script hashes for this domain
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT sha256 FROM scan_scripts WHERE domain = :domain
        """), {"domain": domain})
        all_hashes = [row[0] for row in result.fetchall()]
    if not all_hashes:
        return []
    freq = Counter(all_hashes)
    total = sum(freq.values())
    anomalies = []
    for script in script_hashes:
        h = script["sha256"]
        count = freq.get(h, 0)
        pct = count / total if total > 0 else 0
        if pct < 0.01:
            anomalies.append({
                "id": f"anomaly_{h[:8]}",
                "description": f"Script {script['script_url']} is a new or rare script for this domain.",
                "severity": "medium",
                "sha256": h,
                "occurrence_pct": pct
            })
    return anomalies 