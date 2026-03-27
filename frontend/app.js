// Base Map setup
const rasterLayer = new ol.layer.Tile({
    source: new ol.source.OSM() // Using OpenStreetMap as default for MVP since it's easy and doesn't require API keys
});

const vectorSource = new ol.source.Vector({wrapX: false});
const vectorLayer = new ol.layer.Vector({
    source: vectorSource,
    style: new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(0, 153, 255, 0.2)',
        }),
        stroke: new ol.style.Stroke({
            color: '#0099ff',
            width: 2,
        }),
    }),
});

// Layer for showing Semantic Segmentation
const changesSource = new ol.source.Vector();
const changesLayer = new ol.layer.Vector({
    source: changesSource,
    style: function(feature) {
        const classType = feature.get('class_type') || '';
        let color = 'rgba(255, 0, 0, 0.5)'; // Default Red
        let stroke = 'red';
        
        if (classType.includes('Vegetation')) {
            color = 'rgba(0, 255, 0, 0.5)';
            stroke = 'green';
        }
        
        return new ol.style.Style({
            fill: new ol.style.Fill({ color: color }),
            stroke: new ol.style.Stroke({ color: stroke, width: 3 })
        });
    }
});

const map = new ol.Map({
    target: 'map',
    layers: [rasterLayer, vectorLayer, changesLayer],
    view: new ol.View({
        center: ol.proj.fromLonLat([85.8245, 20.2961]), // Center of Bhubaneswar
        zoom: 12
    })
});

let drawInteractive;
let drawnGeoJSON = null;
const apiBaseUrl = 'http://localhost:8000'; // Make sure backend runs here

document.getElementById('draw-btn').addEventListener('click', () => {
    map.removeInteraction(drawInteractive);
    drawInteractive = new ol.interaction.Draw({
        source: vectorSource,
        type: 'Polygon',
    });
    
    drawInteractive.on('drawend', (event) => {
        const feature = event.feature;
        const geometry = feature.getGeometry();
        // Convert to EPSG:4326 for standard GeoJSON format
        const geom4326 = geometry.clone().transform('EPSG:3857', 'EPSG:4326');
        const format = new ol.format.GeoJSON();
        drawnGeoJSON = format.writeGeometryObject(geom4326);
        
        document.getElementById('analyze-btn').disabled = false;
        map.removeInteraction(drawInteractive);
    });
    
    map.addInteraction(drawInteractive);
});

document.getElementById('clear-btn').addEventListener('click', () => {
    vectorSource.clear();
    changesSource.clear();
    drawnGeoJSON = null;
    document.getElementById('analyze-btn').disabled = true;
    document.getElementById('alert-box').style.display = 'none';
    map.removeInteraction(drawInteractive);
});

document.getElementById('analyze-btn').addEventListener('click', async () => {
    const aoiName = document.getElementById('aoi-name').value || "Unnamed AOI";
    const spinner = document.getElementById('status-spinner');
    const alertBox = document.getElementById('alert-box');
    const alertMessage = document.getElementById('alert-message');
    
    if (!drawnGeoJSON) return;
    
    spinner.classList.remove('d-none');
    document.getElementById('analyze-btn').disabled = true;
    alertBox.style.display = 'none';
    changesSource.clear();

    try {
        // Step 1: Save AOI
        const aoiResponse = await fetch(`${apiBaseUrl}/api/aoi`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: aoiName, geojson: { type: 'Feature', geometry: drawnGeoJSON } })
        });
        
        let aoiData = await aoiResponse.json();
        
        if (aoiResponse.ok) {
            const aoiId = aoiData.aoi_id;
            
            // Step 2: Trigger Analysis with GalaxEye attributes
            const sensorVal = document.getElementById('sensor-type').value;
            const vqaVal = document.getElementById('vqa-query').value;
            
            const reqBody = {
                sensor: sensorVal,
                vqa_query: vqaVal
            };
            
            const analyzeResponse = await fetch(`${apiBaseUrl}/api/analyze/${aoiId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqBody)
            });
            const analyzeData = await analyzeResponse.json();
            
            if (analyzeResponse.ok) {
                // Display changes
                const format = new ol.format.GeoJSON();
                const features = format.readFeatures(analyzeData.changes, {
                    featureProjection: 'EPSG:3857'
                });
                changesSource.addFeatures(features);
                
                // Show Alert
                alertBox.style.display = 'block';
                alertMessage.innerText = analyzeData.message || "Analysis complete.";
            } else {
                alert("Analysis failed: " + JSON.stringify(analyzeData));
            }
        } else {
            alert("Failed to save AOI: " + JSON.stringify(aoiData));
        }
        
    } catch (e) {
        console.error(e);
        alert("Server error. Is the backend running?");
    } finally {
        spinner.classList.add('d-none');
        document.getElementById('analyze-btn').disabled = false;
    }
});
