# Satellite Vision Pipeline MVP 🛰️

A cloud-native, full-stack geospatial pipeline built to demonstrate end-to-end satellite image processing architectures. It highlights the infrastructure needed for **Vision-Language Models (VLMs)**, **Multi-Sensor Data Fusion (SAR/Optical)**, and **Change Detection**.

This project was specifically architected as a Proof of Concept (PoC) for Earth Observation machine learning pipelines, natively connecting front-end user interfaces to AWS-hosted planetary data.

## 🚀 Key Features

*   **Dynamic STAC API Integration**: Directly interfaces with AWS Earth Search (Element84) to query real-time Sentinel-1 (SAR) and Sentinel-2 (Optical) metadata via native REST clients.
*   **Vision-Language Model (VQA) Interface**: Includes a frontend Visual Question Answering (VQA) input that merges user text queries with live satellite metadata to generate contextual captions.
*   **Multi-Class Semantic Segmentation**: Architected to ingest and display multi-class geospatial polygons (e.g., Object Detection for New Structures vs. Semantic Segmentation for Vegetation Clearance).
*   **Spatial Database Storage**: Utilizes PostgreSQL + PostGIS to natively store and query `GeoJSON` bounding boxes.

## 📊 Architecture Flowchart

```mermaid
graph TD
    %% User Interfaces
    subgraph Frontend [Leaflet Web Frontend]
        A[User draws AOI Polygon] --> B[User inputs Visual Question]
        A --> C[User selects Sensor: Optical or SAR]
        B --> D[Click 'Analyze Changes']
        C --> D
    end

    %% Backend Architecture
    subgraph Backend [FastAPI Python Server]
        D -- "POST /api/analyze\n(JSON: Bounding Box, Query, Sensor)" --> E[app.py API Endpoint]
        E -- "ST_GeomFromGeoJSON" --> F[(PostgreSQL Database\nwith PostGIS)]
        E -- "Pass Payload" --> G[processing.py Algorithm]
        
        %% AWS Integration
        G -- "Query Metadata" --> H[AWS Earth Search STAC API]
        H -- "Return Sentinel Image IDs" --> G
        
        %% Mock Logic
        G -- "Format Detections" --> I[Format Multi-class Mock Polygons]
        G -- "Merge VQA Text" --> J[Generate Vision-Language Output]
        
        I --> K[Package GeoJSON & Alert Map]
        J --> K
        K -- "_Returns Feature_Collection_" --> E
    end

    %% Visualization Output
    E -- "HTTP 200 (SUCCESS)" --> L[Update Layer \n& Display VLM Caption]
    
    %% Styling Colors
    style Frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    style Backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    style F fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    style H fill:#fce4ec,stroke:#880e4f,stroke-width:2px;
    style L fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
```

## 💻 Tech Stack
*   **Frontend**: HTML5, Vanilla JS, OpenLayers
*   **Backend**: Python 3.10+, FastAPI, Uvicorn 
*   **Database**: PostgreSQL, PostGIS, `asyncpg`
*   **Geospatial Processing**: Built-in REST STAC integration, GeoJSON parsing

## 🛠️ How to Run Locally

### 1. Database Setup
Make sure you have PostgreSQL running locally with the **PostGIS** extension installed. Create an empty database named `satellite_db`.
   
### 2. Initialize the Tables
```bash
conda activate satellite_mvp
cd backend
python init_db.py
```

### 3. Start the API Server
```bash
uvicorn app:app --reload
```
The server will now accept API connections on `http://127.0.0.1:8000`.

### 4. Launch the Web App
Open your web browser and navigate directly to:
```
http://127.0.0.1:8000/
```
*(FastAPI natively serves the frontend HTML, automatically zooming to Bhubaneswar).*
