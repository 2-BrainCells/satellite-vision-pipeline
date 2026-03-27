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
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryTextColor': '#ffffff', 'lineColor': '#94a3b8'}, 'flowchart': {'nodeSpacing': 50, 'rankSpacing': 60}}}%%
graph TD
    %% Explicit Entry Point
    Start([Start: User Accesses Platform]) --> A

    %% User Interfaces
    subgraph Frontend [Leaflet Web Frontend]
        A[/"Draw Area of Interest Polygon"/]
        B[/"Input Visual Question"/]
        C[/"Select Sensor: Optical or SAR"/]
        D["Click 'Analyze Changes' Button"]
        
        A --> D
        B --> D
        C --> D
    end

    %% Backend Architecture
    subgraph Backend [FastAPI Python Server]
        E("app.py API Endpoint")
        F[("PostgreSQL DB<br>with PostGIS")]
        G["processing.py<br>Algorithm"]
        
        D -- "POST /api/analyze<br>(JSON: BBox, Query, Sensor)" --> E
        
        %% Database Interaction
        E -- "ST_GeomFromGeoJSON" --> F
        
        %% Core Processing Engine
        E -- "Pass Payload" --> G
        
        %% External Cloud API
        H{{"AWS Earth Search<br>STAC API"}}
        G -- "Translate Bounding Box<br>& Query Metadata" --> H
        H -- "Return Clearest<br>Sentinel IDs & Dates" --> G
        
        %% The GalaxEye Edge Features
        I["Generate Object Detection<br>& Semantic Segmentation"]
        J["Generate Vision-Language Output<br>& Merge VQA Text"]
        K["Package GeoJSON<br>& Alert Map"]
        
        G --> I
        G --> J
        I --> K
        J --> K
        
        %% Finalization
        K -- "Returns Feature_Collection" --> E
        E -- "Log Output History" --> F
    end

    %% Visualization Output
    L[/"Update UI Map Layers<br>& Display VLM Caption Alert"/]
    E -- "HTTP 200 SUCCESS" --> L
    
    %% Explicit Exit Point
    End([End: User Views Insights])
    L --> End

    %% Dark Mode Styling Colors
    style Start fill:#083344,stroke:#22d3ee,stroke-width:2px,color:#fff
    style End fill:#083344,stroke:#22d3ee,stroke-width:2px,color:#fff
    
    %% Subgraph Styling
    style Frontend fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style Backend fill:#064e3b,stroke:#4ade80,stroke-width:2px,color:#fff
    
    %% Specific Node Styling
    style F fill:#7c2d12,stroke:#fb923c,stroke-width:2px,color:#fff
    style H fill:#831843,stroke:#f472b6,stroke-width:2px,color:#fff
    style L fill:#4c1d95,stroke:#c084fc,stroke-width:2px,color:#fff
    
    %% Ensure base nodes inside subgraphs have dark backgrounds and light text
    classDef default fill:#1e293b,stroke:#64748b,stroke-width:1px,color:#f8fafc;
    class A,B,C,D,E,G,I,J,K default;
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
