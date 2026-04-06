import requests
import os
from database import SessionLocal
from models.customer import Customer

FLASK_API = os.getenv("FLASK_API", "http://mock-server:5000/api/customers")

def fetch_all_customers():
    page = 1
    limit = 10
    all_data = []
    while True:
        res = requests.get(FLASK_API, params={"page": page, "limit": limit})
        if res.status_code != 200:
            raise Exception("Failed to fetch from Flask")
        json_data = res.json()
        data = json_data.get("data", [])
        if not data:
            break
        all_data.extend(data)
        if len(data) < limit:
            break
        page += 1
    return all_data

def upsert_customer(db, data):
    existing = db.query(Customer).filter(Customer.customer_id == str(data["customer_id"])).first()
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
    else:
        customer = Customer(**data)
        db.add(customer)
    db.commit()
