# Satellite Vision Pipeline MVP Documentation

This document outlines the detailed workflow, functionalities, edge cases, and future roadmap of the Satellite Vision Pipeline project.

## 🌟 Core Functionalities

The application serves as a Proof of Concept (PoC) for Earth Observation machine learning pipelines. The primary features include:

1. **Interactive Spatial Mapping:** An OpenLayers map interface that allows users to seamlessly draw Area of Interest (AOI) polygons.
2. **Dynamic STAC querying:** Automatically interrogates AWS Earth Search (Element84) STAC APIs to retrieve real-time Sentinel-1 (SAR) and Sentinel-2 (Optical) imagery metadata.
3. **True Pixel Differencing (Raster Processing):** Utilizes `rasterio` to stream multi-temporal raster arrays over designated geometries, dynamically extracting numeric thresholds to establish pixel anomalies.
4. **Geospatial Morphology:** Processes raster masks into simplified, buffered vector polygons bound perfectly within the user's initialized AOI.
5. **Multi-Class Detection Visuals:** Assigns dynamic color-coded styles on the front end—e.g., Red for New Structures and Yellow for Vegetation Clearance.
6. **Robust Graceful Fallbacks:** Simulates and mocks results if heavy remote-sensing libraries (`gdal/rasterio`) fail to deploy, ensuring continuous demo capabilities.
7. **Simulation of a Vision-Language Model (VQA Mode):** Clicking visual anomalies brings up a Visual Question Answering component that routes context-specific queries to the backend.

---

## ⚙️ Detailed Code Workflow

### 1. User Inputs & Initialization
- **Frontend (`app.js` & `index.html`):** The user enters an explicitly named location, establishes a `Start Date` and `End Date`, and dictates the desired satellite constellation explicitly (Optical vs. SAR). 
- Using `ol.interaction.Draw`, they outline a polygon bounding box (AOI) on the map interface.
- Clicking the `Analyze Changes` button fires a `POST` request to the backend with the polygon geometry formatted as `GeoJSON`.

### 2. Geometry Registration (Database Layer)
- **Backend API (`app.py` via `api/aoi` route):** The GeoJSON is captured and securely inserted into the PostgreSQL `satellite_db`.
- PostGIS functions (`ST_SetSRID`, `ST_GeomFromGeoJSON`) natively format the JSON structure into valid spatial data types. 
- The row ID is returned back to the UI.

### 3. Core Change Detection
- The UI triggers `POST /api/analyze/{aoi_id}`.
- **Data Acquisition (`processing.py`):** The system constructs a strict Cloud-Native REST query to AWS Earth Search targeting the exact bounding box and date ranges. The system forces a cloud-cover ceiling (`"eo:cloud_cover": {"lt": 5}`) for Optical data.
- **Raster Streaming:** The system extracts the oldest and newest items from the STAC items context. It accesses the `href` URLs of the actual `nir` (Near-Infrared) or `vv` (SAR Polarization) bands.
- **Matrix Mathematics:** `rasterio` creates arrays of the designated window. A NumPy scalar standard deviation threshold filters for dramatic temporal changes between the two arrays: `change_mask = (np.abs(diff) > threshold).astype('uint8')`.
- **Polygon Clipping:** Open-source `shapely` and `rasterio.features` map out mathematical shapes based on the generated masks. These geometries are smoothed, buffered, and strictly intersected against the user's initial boundary constraints to prevent spilling visual glitches outward.
- **Database Logging:** `app.py` registers the newly derived vectors directly into an `alerts` PostgreSQL table.

### 4. Visual Layout & Context Generation (VQA)
- Geospatial annotations are dynamically laid over the map UI. 
- When the user selects a generated anomaly, the frontend extracts that specific geometric chunk.
- The user inputs a text question regarding the anomaly. This context is funneled (`POST /api/vqa`) into a placeholder routing function meant to model modern VLMs (Vision-Language Models). The simulated LLM dictates the localized terrain structure textually.

---

## 🛠️ Edge Cases Handled

* **Lack of STAC Cloud Coverage Dates:** If the system is queried over a highly dense cloud-covered timeframe leading to zero matches, it catches the bounds mathematically natively, throwing a clean error instead of unhandled HTTP 500s.
* **Network Failures / Deployment Import Limitations:** If the container natively fails to compile `GDAL` or `rasterio`, the system detects `import error` blocks via `HAS_RASTERIO=False`. The application instantly pivots to a gracefully mocked bounding box pipeline.
* **Math Glitches (Polylines outside constraints):** The backend actively drops any smoothed geometry mapping that inadvertently extrudes entirely outside the mapped user AOI (`if smoothed_shape.is_empty: continue`).
* **Frontend Overlaps:** Prevents UI freezing by forcing specific boolean button locks and loading spinners during intensive fetch operations.

## ⚠️ Edge Cases Unhandled (Current MVP Limitations)

* **Giant Bounding Box Overloads:** Users explicitly constructing gigabyte-scale map windows will natively crash connection timeouts. The backend currently lacks a strict bounding-area restriction check against spatial sizes dynamically.
* **Monsoon Cloud Coverage:** Forcing `lt: 5` cloud coverage logic may cause endless dry loops where regions cannot physically acquire clear arrays between ranges. 
* **Concurrent Memory Overloading:** NumPy floats mapping parallelized users could exceed small-container RAM dynamically.

---

## 🚀 Future Scope & Scaling

1. **Job Queue Architecture (Asynchronous Scaling):** Raster arrays fundamentally take vast amounts of compute. Re-architecting FastAPI into a `Celery/Redis` messaging broker will allow users to submit tasks and return back when processing completes dynamically, unlocking infinite horizontal scaling.
2. **Actual Vision Language Multi-Modal Logic:** Transition the `perform_vlm_query` to construct actual image chips representing the bounding box coordinates using raw AWS S3 buckets. Expose these encoded JPEG chips into Claude 3 Opus, GPT-4V, or LLaVA pipelines.
3. **True Semantic Segmentation:** Transition pure numpy differencing to an AWS SageMaker endpoint running UNet architectures or YOLO-v8 segmentation models capable of distinctly classifying "Buildings" vs. "Flooded Water" explicitly.
4. **Time-Series Analysis:** Query STAC metadata for the entire history of an area (20+ images) to chart time-series graphs (e.g., NDVI index decay) instead of locking users directly to Start/End benchmarks.
5. **SAR Coherence Data:** Use complex Sentinel-1 Single Look Complex (SLC) images to measure structural ground deformation (interferometry), enabling precise earthquake or structural settling metrics instead of just utilizing raw amplitude differences.
