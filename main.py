import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import create_document, get_documents, db
from schemas import Lead

app = FastAPI(title="OmSai Packers & Movers API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "OmSai Packers & Movers backend is running"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Public content endpoints (static content for the site)
class Testimonial(BaseModel):
    name: str
    text: str

@app.get("/content/testimonials", response_model=List[Testimonial])
def get_testimonials():
    return [
        {"name": "Rahul S.", "text": "Very professional team. My Mumbai to Pune move was smooth and on time."},
        {"name": "Anita K.", "text": "They packed everything carefully and delivered safely. Highly recommend!"},
        {"name": "Vikram P.", "text": "Affordable and reliable. Great communication throughout the process."}
    ]

@app.get("/content/services")
def get_services():
    return [
        {"title": "Household Shifting", "desc": "End-to-end packing, loading, moving, unloading and unpacking for local and domestic moves."},
        {"title": "Office Relocation", "desc": "Minimal downtime office moves with careful handling of equipment and files."},
        {"title": "Vehicle Transport", "desc": "Door-to-door car and bike transport with transit insurance options."},
        {"title": "Storage & Warehousing", "desc": "Clean, secure short and long term storage solutions with inventory management."}
    ]

# Lead capture endpoints
@app.post("/leads")
def create_lead(lead: Lead):
    try:
        lead_id = create_document("lead", lead)
        return {"status": "success", "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leads")
def list_leads(limit: Optional[int] = 50):
    try:
        docs = get_documents("lead", limit=limit)
        # Convert ObjectId and datetime to strings for JSON
        def serialize(doc):
            doc["_id"] = str(doc.get("_id"))
            for k, v in list(doc.items()):
                if isinstance(v, datetime):
                    doc[k] = v.isoformat()
            return doc
        return [serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
