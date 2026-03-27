# Satellite Change Detection MVP

This is an MVP application for detecting simulated changes in a user-defined Area of Interest (AOI).

## Prerequisites
1. **Python 3.10+**: You need conda or a Python virtual environment. Environment `satellite_mvp` is already created.
2. **PostgreSQL with PostGIS**: Install PostgreSQL and the PostGIS spatial extension.
3. Database `satellite_db` created locally, with credentials `postgres` / `postgres`.

## Step 1: Initialize the Database
1. Open pgAdmin or a SQL client and create a new database named `satellite_db`.
2. Ensure you have the PostGIS extension built for it (or the init script will try to create it).
3. Initialize the schema using the Python script (from within the backend directory):
   ```bash
   conda activate satellite_mvp
   cd backend
   python init_db.py
   ```

## Step 2: Run the Backend API
Start the FastAPI server:
```bash
conda activate satellite_mvp
cd backend
uvicorn app:app --reload --port 8000
```

## Step 3: Open the Frontend
Simply open the `index.html` file in your preferred web browser:
```bash
# In Windows for example:
start ../frontend/index.html
```
Or open the file in Chrome/Edge directly.

## Usage
- Click **Draw Polygon** to create an AOI on the map.
- Give it a name and click **Analyze Changes**.
- You will see the backend mock response highlighting changed areas and triggering an alert.
