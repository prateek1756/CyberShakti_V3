import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_mule_transactions_json():
    payload = {
        "transactions": [
            {"sender": "VICTIM_01", "receiver": "MULE_01", "amount": 100000},
            {"sender": "VICTIM_02", "receiver": "MULE_01", "amount": 150000},
            {"sender": "MULE_01", "receiver": "LAYERING_01", "amount": 240000},
            {"sender": "LAYERING_01", "receiver": "CASHOUT_01", "amount": 230000}
        ]
    }
    response = client.post("/api/v1/detect/analyze-mule-transactions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert "graph_data" in data
    summary = data["graph_data"]["summary"]
    assert summary["total_accounts"] == 5
    assert summary["flagged_mules"] >= 1
    assert summary["total_volume"] == 720000.0

def test_analyze_mule_csv_upload():
    csv_content = (
        "sender,receiver,amount,timestamp\n"
        "ACC_01,MULE_100,50000,2026-08-22 10:00:00\n"
        "ACC_02,MULE_100,75000,2026-08-22 10:05:00\n"
        "MULE_100,DEST_99,120000,2026-08-22 10:15:00\n"
    )
    files = {"file": ("test_transactions.csv", csv_content, "text/csv")}
    response = client.post("/api/v1/detect/analyze-mule-csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["transactions_parsed"] == 3
    assert "graph_data" in data
    assert data["graph_data"]["summary"]["total_accounts"] == 4
