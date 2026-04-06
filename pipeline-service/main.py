from fastapi import FastAPI, HTTPException
from services.ingestion import fetch_all_customers, upsert_customer
from database import SessionLocal, engine
from models.customer import Base, Customer

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post("/api/ingest")
def ingest():
    db = SessionLocal()
    try:
        customers = fetch_all_customers()
        for c in customers:
            upsert_customer(db, c)
        return {"status": "success", "records_processed": len(customers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/customers")
def get_customers(page: int = 1, limit: int = 10):
    db = SessionLocal()
    offset = (page - 1) * limit
    data = db.query(Customer).offset(offset).limit(limit).all()
    return {"data": [c.__dict__ for c in data], "page": page, "limit": limit}

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str):
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.__dict__
