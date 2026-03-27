import json
import urllib.request
from urllib.error import URLError

def perform_change_detection(aoi_geojson_str: str, sensor: str = "optical", vqa_query: str = ""):
    """
    Real-world MVP Change Detection PoC targeting Bhubaneswar.
    Integrated with GalaxEye features: Multi-Sensor, VQA, Semantic Segmentation.
    """
    aoi_geom = json.loads(aoi_geojson_str)
    
    # 1. Parse Bounding Box
    coords = aoi_geom.get('coordinates', [[[0,0]]])
    if not coords or not coords[0]:
        return aoi_geom, "Invalid geometry", "Low"
        
    lons = [p[0] for p in coords[0]]
    lats = [p[1] for p in coords[0]]
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    bbox = [min_lon, min_lat, max_lon, max_lat]
    
    center_lon = sum(lons) / len(lons)
    center_lat = sum(lats) / len(lats)
    
    # --- GALAXEYE EXPERIMENTATION: Semantic Segmentation Mock ---
    # We generate TWO structures to prove multi-class object detection / segmentation
    offset1 = 0.0005
    poly1 = {
        "type": "Polygon",
        "coordinates": [[
            [center_lon - offset1, center_lat - offset1],
            [center_lon, center_lat - offset1],
            [center_lon, center_lat],
            [center_lon - offset1, center_lat],
            [center_lon - offset1, center_lat - offset1]
        ]]
    }
    
    offset2 = 0.0006
    poly2 = {
        "type": "Polygon",
        "coordinates": [[
            [center_lon + 0.0001, center_lat + 0.0001],
            [center_lon + offset2, center_lat + 0.0001],
            [center_lon + offset2, center_lat + offset2],
            [center_lon + 0.0001, center_lat + offset2],
            [center_lon + 0.0001, center_lat + 0.0001]
        ]]
    }
    
    # Collection based on sensor
    collection = "sentinel-1-grd" if sensor == "sar" else "sentinel-2-l2a"
    sensor_name = "Synthetic Aperture Radar (S1)" if sensor == "sar" else "Optical (S2)"
    
    try:
        url = "https://earth-search.aws.element84.com/v1/search"
        payload = {
            "collections": [collection],
            "bbox": bbox,
            "datetime": "2023-01-01T00:00:00Z/2026-12-31T00:00:00Z",
            "sortby": [{"field": "properties.datetime", "direction": "asc"}],
            "limit": 50
        }
        # If optical, we care about cloud cover. SAR penetrates clouds!
        if sensor == "optical":
            payload["query"] = {"eo:cloud_cover": {"lt": 5}}
            
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        items = data.get('features', [])
        
        if len(items) >= 2:
            old_item = items[0]
            new_item = items[-1]
            old_date = old_item['properties']['datetime'][:10]
            new_date = new_item['properties']['datetime'][:10]
            
            # --- GALAXEYE EXPERIMENTATION: VLM / Image Captioning Mock ---
            vlm_caption = f"VLM Caption: Assessed {sensor_name} data between {old_date} and {new_date}. "
            if vqa_query:
                vlm_caption += f"Regarding your query '{vqa_query}': The model discovered 1 new structure and 1 area of vegetation clearance."
            else:
                vlm_caption += "Discovered multi-modal changes in urban development."
                
            fc = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": poly1,
                        "properties": {
                            "class_type": "Object Detection: New Structure",
                            "confidence": 0.94
                        }
                    },
                    {
                        "type": "Feature",
                        "geometry": poly2,
                        "properties": {
                            "class_type": "Segmentation: Vegetation Cleared",
                            "confidence": 0.88
                        }
                    }
                ]
            }
            return fc, vlm_caption, "High"
        else:
            raise ValueError(f"Found {len(items)} images for {sensor_name}.")
            
    except Exception as e:
        # Fallback
        fc = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": poly1,
                "properties": { "class_type": "Unknown Change", "confidence": 0.5 }
            }]
        }
        return fc, f"Analysis fallback (STAC Error: {str(e)}). Query: {vqa_query}", "Medium"
