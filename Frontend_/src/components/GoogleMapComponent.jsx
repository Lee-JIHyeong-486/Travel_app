import { useEffect, useRef } from "react";

export default function GoogleMapComponent({ places, routeGeoJson }) {
    const mapRef = useRef(null);
    // GeoJSON → Google Maps LatLng[] 변환 함수
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
            const script = document.createElement("script");
            const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`;
            script.async = true;
            script.defer = true;
            script.onload = drawMap;
            document.head.appendChild(script);
        };

        const drawMap = () => {
            const map = new window.google.maps.Map(mapRef.current, {
                center: {
                    lat: places[0].location.latitude,
                    lng: places[0].location.longitude,
                },
                zoom: 13,
            });

            places.forEach((place) => {
                const marker = new window.google.maps.Marker({
                    position: {
                        lat: place.location.latitude,
                        lng: place.location.longitude,
                    },
                    map,
                    title: place.name,
                });

                const infoWindow = new window.google.maps.InfoWindow({
                    content: `
                        <div>
                            <strong>${place.name}</strong><br/>
                            Concept: ${place.concept}<br/>
                            Address: ${place.address || "N/A"}
                        </div>
                    `,
                });

                marker.addListener("click", () => {
                    infoWindow.open(map, marker);
                });
            });
// 경로선 표시
            if (routeGeoJson) {
                const path = convertGeoJsonToPath(routeGeoJson);
                new window.google.maps.Polyline({
                    path,
                    geodesic: true,
                    strokeColor: "#FF0000",
                    strokeOpacity: 1.0,
                    strokeWeight: 4,
                    map: map,
                });
            }        
        };

        if (!window.google || !window.google.maps) {
            loadGoogleMaps();
        } else {
            drawMap();
        }
    }, [places, routeGeoJson]); // routeGeoJson도 의존성에 추가

    return (
        <div
            ref={mapRef}
            style={{ width: "100%", height: "300px" }}
            className="rounded shadow"
        />
    );
}