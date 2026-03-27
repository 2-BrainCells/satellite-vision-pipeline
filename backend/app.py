from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
from typing import Any, Dict
from fastapi.staticfiles import StaticFiles
from processing import perform_change_detection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://postgres:Hello@localhost:5432/satellite_db" # Update manually if needed

class AOIPayload(BaseModel):
    name: str
    geojson: Dict[str, Any]

class AnalyzePayload(BaseModel):
    sensor: str = "optical"
    vqa_query: str = ""

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

@app.post("/api/aoi")
async def save_aoi(payload: AOIPayload):
    pool = app.state.pool
    
    # Simple extraction of the polygon geometry as EWKT or just passing GeoJSON into ST_GeomFromGeoJSON
    import json
    geom_json = json.dumps(payload.geojson['geometry'])
    
    async with pool.acquire() as connection:
        aoi_id = await connection.fetchval(
            """
            INSERT INTO aois (name, geom) 
            VALUES ($1, ST_SetSRID(ST_GeomFromGeoJSON($2), 4326)) 
            RETURNING id
            """,
            payload.name, geom_json
        )
    return {"status": "success", "aoi_id": aoi_id}

@app.post("/api/analyze/{aoi_id}")
async def analyze_aoi(aoi_id: int, payload: AnalyzePayload):
    sensor = payload.sensor
    vqa_query = payload.vqa_query
    
    pool = app.state.pool
    async with pool.acquire() as connection:
        # Fetch AOI geometry
        record = await connection.fetchrow("SELECT ST_AsGeoJSON(geom) as geom_json FROM aois WHERE id = $1", aoi_id)
        if not record:
            raise HTTPException(status_code=404, detail="AOI not found")
        
        # Pass the sensor and VQA query to processing
        changes_geojson, message, severity = perform_change_detection(record['geom_json'], sensor, vqa_query)

        # Create alert if changes found
        alert_id = await connection.fetchval(
            """
            INSERT INTO alerts (aoi_id, change_type, severity, message)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            aoi_id, "Vegetation/Anthropogenic", severity, message
        )
        
    return {"status": "success", "alert_id": alert_id, "changes": changes_geojson, "message": message}

# Mount the frontend directory to serve static files (index.html, JS, CSS)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
