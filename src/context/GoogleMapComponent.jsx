// src/components/GoogleMapComponent.jsx
import { useEffect, useRef } from "react";

export default function GoogleMapComponent({ places, routeGeoJson = null }) {
    const mapRef = useRef(null);
    const mapInstance = useRef(null); // 지도 객체 저장
    const markersRef = useRef([]);
    const polylineRef = useRef(null);

    const getLatLngObj = (location) => ({
        lat: location?.latitude ?? 37.5665,
        lng: location?.longitude ?? 126.9780,
    });

    // GeoJSON 좌표 → LatLng 객체 배열로 변환
    const convertGeoJsonToPath = (geojson) => {
        try {
            const coords = geojson.features[0].geometry.coordinates;
            return coords.map(([lng, lat]) => ({ lat, lng }));
        } catch (err) {
            console.error("경로 변환 실패", err);
            return [];
        }
    };

    useEffect(() => {
        if (!places || places.length === 0) return;

        const loadGoogleMaps = () => {
            if (document.getElementById("google-maps-script")) {
                drawMap();
                return;
            }

            const script = document.createElement("script");
            script.id = "google-maps-script";
            script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`;
            script.async = true;
            script.defer = true;
            script.onload = drawMap;
            document.head.appendChild(script);
        };

        const drawMap = () => {
            const center = getLatLngObj(places[0].location);
            mapInstance.current = new window.google.maps.Map(mapRef.current, {
                center,
                zoom: 13,
            });

            // 마커 그리기
            markersRef.current.forEach((m) => m.setMap(null));
            markersRef.current = [];

            places.forEach((place) => {
                const marker = new window.google.maps.Marker({
                    position: getLatLngObj(place.location),
                    map: mapInstance.current,
                    title: place.name,
                });

                const infoWindow = new window.google.maps.InfoWindow({
                    content: `
                        <div style="font-size: 14px; line-height: 1.4">
                            <strong>${place.name}</strong><br/>
                            ${place.concept?.join(", ") || ""}
                        </div>
                    `,
                });

                marker.addListener("click", () => {
                    infoWindow.open(mapInstance.current, marker);
                });

                markersRef.current.push(marker);
            });

            // Polyline 경로 그리기
            if (routeGeoJson) {
                const path = convertGeoJsonToPath(routeGeoJson);
                if (path.length > 1) {
                    if (polylineRef.current) {
                        polylineRef.current.setMap(null);
                    }
                    polylineRef.current = new window.google.maps.Polyline({
                        path,
                        map: mapInstance.current,
                        strokeColor: "#007BFF",
                        strokeOpacity: 0.8,
                        strokeWeight: 4,
                    });
                }
            }
        };

        if (!window.google || !window.google.maps) {
            loadGoogleMaps();
        } else {
            drawMap();
        }
    }, [places, routeGeoJson]);

    return (
        <div
            ref={mapRef}
            style={{ width: "100%", height: "100%" }}
            className="rounded shadow"
        />
    );
}