import React, { useState, useEffect } from 'react';
import { Navigation } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Radar.css';

// Custom icon for the user (Proud yellow, glowing)
const userIcon = new L.DivIcon({
    className: 'user-marker-icon',
    html: `<div style="background-color: #FFC107; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #1A1D24; box-shadow: 0 0 10px rgba(255,193,7,0.8);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
});

// Custom icon for the store (Dark card, yellow pin)
const storeIcon = new L.DivIcon({
    className: 'store-marker-icon',
    html: `
        <div style="
            background-color: var(--bg-card); 
            border: 2px solid var(--color-primary); 
            border-radius: 50% 50% 50% 0; 
            width: 24px; 
            height: 24px; 
            transform: rotate(-45deg); 
            display: flex; 
            align-items: center; 
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        ">
            <div style="background-color: var(--color-primary); width: 8px; height: 8px; border-radius: 50%;"></div>
        </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    tooltipAnchor: [14, -14]
});

// Helper component to center map on bounds
const FitBounds = ({ bounds }) => {
    const map = useMap();
    useEffect(() => {
        if (bounds && bounds.length > 0) {
            map.fitBounds(bounds, { padding: [40, 40] }); // Add padding so markers aren't at the very edge
        }
    }, [bounds, map]);
    return null;
};

const Radar = ({ storeName = "Albert", fallbackWalkTime = "Calc..." }) => {
    const [userPos, setUserPos] = useState(null);
    const [storePos, setStorePos] = useState(null);
    const [routeLine, setRouteLine] = useState([]);
    const [walkTime, setWalkTime] = useState(fallbackWalkTime);
    const [errorMsg, setErrorMsg] = useState('');
    const [mapBounds, setMapBounds] = useState(null);

    // 1. Get User Location
    useEffect(() => {
        if (!navigator.geolocation) {
            setErrorMsg("Geolocation not supported");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = [position.coords.latitude, position.coords.longitude];
                setUserPos(pos);
                // Initially set bounds to just the user
                setMapBounds([pos, pos]);
            },
            (error) => {
                console.error("Error getting location:", error);
                setErrorMsg("Location access denied. Using default.");
                const defaultPos = [50.0755, 14.4378];
                setUserPos(defaultPos); // Default to Prague center
                setMapBounds([defaultPos, defaultPos]);
            }
        );
    }, []);

    // 2. Geocode Store & 3. Calculate Route
    useEffect(() => {
        if (!userPos || !storeName) return;

        const findStoreAndRoute = async () => {
            try {
                // Step A: Geocode the store near the user using Nominatim (OpenStreetMap)
                const cleanStoreName = storeName.split('(')[0].trim();

                // Create a bounding box (~10km) around the user to strictly limit the search area
                // 1 degree latitude = ~111km, 1 degree longitude (at 50deg lat) = ~71km
                const latOffset = 0.1; // ~11km
                const lonOffset = 0.15; // ~10km
                const lat1 = userPos[0] - latOffset;
                const lat2 = userPos[0] + latOffset;
                const lon1 = userPos[1] - lonOffset;
                const lon2 = userPos[1] + lonOffset;
                // viewbox format: left,top,right,bottom (lon1,lat2,lon2,lat1)
                const viewbox = `${lon1},${lat2},${lon2},${lat1}`;

                // Use bounded=1 to strictly enforce the viewbox, and countrycodes=cz
                const geocodeUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cleanStoreName)}&limit=15&viewbox=${viewbox}&bounded=1&countrycodes=cz`;

                const geoRes = await fetch(geocodeUrl);
                const geoData = await geoRes.json();

                if (!geoData || geoData.length === 0) {
                    setErrorMsg("Store location not found nearby");
                    return;
                }

                // Helper: Calculate simple Euclidean distance between two [lat, lon] points
                const calculateDistance = (pos1, pos2) => {
                    const dx = pos1[0] - pos2[0];
                    const dy = pos1[1] - pos2[1];
                    return Math.sqrt(dx * dx + dy * dy);
                };

                // Find the absolute closest store out of all results
                let closestStorePos = null;
                let minDistance = Infinity;

                for (const location of geoData) {
                    const pos = [parseFloat(location.lat), parseFloat(location.lon)];
                    const dist = calculateDistance(userPos, pos);
                    if (dist < minDistance) {
                        minDistance = dist;
                        closestStorePos = pos;
                    }
                }

                setStorePos(closestStorePos);

                // Update bounds to include both user and store
                setMapBounds([userPos, closestStorePos]);

                // Step B: Calculate DRIIVNG route using OSRM
                // Changed from 'foot' to 'driving' because some distances might be far
                // Note: OSRM uses Longitude, Latitude order
                const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${userPos[1]},${userPos[0]};${closestStorePos[1]},${closestStorePos[0]}?overview=full&geometries=geojson`;

                const routeRes = await fetch(osrmUrl);
                const routeData = await routeRes.json();

                if (routeData.code === "Ok" && routeData.routes.length > 0) {
                    const route = routeData.routes[0];

                    // Format distance (OSRM provides distance in meters)
                    const kmDistance = (route.distance / 1000).toFixed(1);
                    const durationSeconds = route.duration; // duration in seconds

                    let formattedTime;
                    if (durationSeconds > 3600) { // If over an hour
                        const hours = Math.floor(durationSeconds / 3600);
                        const minutes = Math.ceil((durationSeconds % 3600) / 60);
                        formattedTime = `${hours} h ${minutes} m`;
                    } else if (durationSeconds > 60) { // If over a minute
                        const minutes = Math.ceil(durationSeconds / 60);
                        formattedTime = `${minutes} min`;
                    } else {
                        formattedTime = `<1 min`;
                    }

                    // Decide whether to show time or distance based on the instruction
                    // "If distance is large or driving time is over 60 mins, render it as X h Y m or X km."
                    // The provided snippet only sets kmDistance, so we'll prioritize that for now.
                    // If the route is very short, we can show time, otherwise distance.
                    if (durationSeconds < 300) { // Less than 5 minutes, show time
                        setWalkTime(formattedTime);
                    } else { // Otherwise, show distance
                        setWalkTime(`${kmDistance} km`);
                    }

                    // Convert GeoJSON (Lon, Lat) back to Leaflet (Lat, Lon) Array
                    const leafletCoords = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
                    setRouteLine(leafletCoords);

                    // Update bounds to include the whole route polyline
                    setMapBounds(leafletCoords);
                }

            } catch (err) {
                console.error("Routing error:", err);
            }
        };

        findStoreAndRoute();
    }, [userPos, storeName]);

    // Initial center before user logs in
    const mapCenter = userPos || [50.0755, 14.4378];

    return (
        <div className="radar-container">

            <MapContainer
                center={mapCenter}
                zoom={14}
                zoomControl={true}
                attributionControl={false}
                scrollWheelZoom={true}
                dragging={true}
                className="radar-map"
            >
                <FitBounds bounds={mapBounds} />

                {/* Dark Mode CartoDB TileLayer */}
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {/* Render Route if available */}
                {routeLine.length > 0 && (
                    <Polyline positions={routeLine} color="#FFC107" weight={4} dashArray="8, 8" opacity={0.8} />
                )}

                {/* Destination Marker */}
                {storePos && (
                    <Marker position={storePos} icon={storeIcon}>
                        <Tooltip permanent direction="top" className="store-tooltip" offset={[0, 0]}>
                            {storeName.split('(')[0].trim()}
                        </Tooltip>
                    </Marker>
                )}

                {/* User Marker */}
                {userPos && (
                    <Marker position={userPos} icon={userIcon} />
                )}

            </MapContainer>

            {/* Glassmorphism Info Pill */}
            <div className="radar-info">
                <div className="nav-icon-wrapper">
                    <Navigation size={18} className="nav-icon" fill="currentColor" />
                </div>
                <div className="nav-text">
                    <span className="nav-label">Next Stop</span>
                    <span className="nav-store">{storeName.split('(')[0].trim()}</span>
                </div>
                <div className="nav-time">
                    {errorMsg && !routeLine.length ? "No Route" : walkTime}
                </div>
            </div>
        </div>
    );
};

export default Radar;
