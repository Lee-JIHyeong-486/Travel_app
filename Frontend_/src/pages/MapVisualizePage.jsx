import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import GoogleMapComponent from "../components/GoogleMapComponent";
import ScheduleViewer from "../components/ScheduleViewer";
import styles from "./MapVisualize.module.css";

export default function MapVisualize() {
    const { state } = useLocation();
    const navigate = useNavigate();
    const travelPlan = state?.travelPlan;
    const userRequest = state?.userRequest; // if userRequest is null, then this is called by savePage.jsx. Disable save button and feedback button
    const [selectedDayIndex, setSelectedDayIndex] = useState(0);
    const [routeGeoJson, setRouteGeoJson] = useState(null);
    const [feedback, setFeedback] = useState("");
    const [loadingRoute, setLoadingRoute] = useState(false);
    const [currentPlaces, setCurrentPlaces] = useState([]);
    const [segmentRoutes, setSegmentRoutes] = useState([]);

    const savePlan = async () => {
    try {
        const response = await axios.post("http://localhost:8000/api/save_plan", {
            user_req: userRequest,
            travel_plan: travelPlan,
        });

        if (response.data.success) {
            alert("일정이 성공적으로 저장되었습니다.");
        } else {
            alert("일정 저장에 실패했습니다: " + (response.data.message || ""));
        }
    } catch (error) {
            console.error("Error saving plan:", error);
            alert("서버 오류로 인해 일정을 저장할 수 없습니다.");
    }
    navigate("/saved");
    };

    const getLatLngObj = (location) => ({
        lat: location?.latitude ?? 37.5665,
        lng: location?.longitude ?? 126.9780,
    });

    const getORSCoords = (list) =>
        list.map((v) => [v.location.longitude, v.location.latitude]);

    useEffect(() => {
        if (!travelPlan?.plans || travelPlan.plans.length === 0) return;

        const day = travelPlan.plans[selectedDayIndex];
        const places = day?.place_to_visit || [];

        setCurrentPlaces(places);
        setRouteGeoJson(null);

        const fetchRoute = async () => {
            if (places.length < 2) return;

            setLoadingRoute(true);
            try {
                const res = await axios.post("http://localhost:8000/api/ors_proxy", {
                    coordinates: getORSCoords(places),
                });
                setRouteGeoJson(res.data);
                
                const segments = res.data.features?.[0]?.properties?.segments;
                if (segments) {
                    setSegmentRoutes(segments);
                    console.log("✅ segmentRoutes 저장됨:", segments); // 디버깅 로그
                } else {
                    setSegmentRoutes([]);
                    console.warn("⚠️ segment 정보가 없습니다.");
                }

            } catch (err) {
                console.error("Route fetch failed", err);
                setRouteGeoJson(null);
            } finally {
                setLoadingRoute(false);
            }
        };

        fetchRoute();
    }, [selectedDayIndex, travelPlan]);

    const handleRetry = async () => {
        const updatedUserData = {
            ...userRequest,
            extra_request: feedback,
        };
        navigate("/loading", { state: { userRequest: updatedUserData } });
    };

    // 조건부 렌더링
    if (!travelPlan?.plans || travelPlan.plans.length === 0) {
        return (
            <div className={styles.errorContainer}>
                <h2>Error</h2>
                <p>No day plans found in the travel plan.</p>
                <button onClick={() => navigate(-1)}>Go Back</button>
            </div>
        );
    }

    return (
        <div className={styles.pageContainer}>
            <div className={styles.title}>저기어때 – AI 여행 가이드</div>

            <div className={styles.gridContainer}>
                <div className={styles.scheduleBox}>
                    <div className={styles.sectionTitle}>일정</div>
                    <select
                        onChange={(e) => setSelectedDayIndex(Number(e.target.value))}
                        value={selectedDayIndex}
                        className={styles.daySelect}
                    >
                        {travelPlan.plans.map((day, i) => (
                            <option key={i} value={i}>
                                Day {i + 1}: {day.date}
                            </option>
                        ))}
                    </select>
                    {loadingRoute && <p>Loading route...</p>}

                    <ScheduleViewer 
                        places={currentPlaces} 
                        segments={segmentRoutes} 
                    />

                </div>

                <div className={styles.mapBox}>
                    <div className={styles.sectionTitle}>지도</div>
                    {currentPlaces.length > 0 && (
                        <GoogleMapComponent
                            places={currentPlaces}
                            routeGeoJson={routeGeoJson}
                        />
                    )}
                </div>
            </div>

            <div className={styles.sectionTitle}>수정 사항</div>
            <textarea
                className={styles.feedbackBox}
                rows={3}
                placeholder="수정사항을 입력해주세요."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
            />

            <div className={styles.buttonRow}>
                <button className={styles.navButton} onClick={() => navigate("/")}>
                    메인메뉴로 돌아가기
                </button>
                <button className={styles.navButton} onClick={savePlan} disabled={!userRequest}>
                    일정 저장하기
                </button>
            </div>

            <div className={styles.retrySection}>
                <h3 className={styles.retryTitle}>피드백 기반 재시도</h3>
                <button
                    className={styles.retryButton}
                    disabled={!(feedback && userRequest)}
                    onClick={handleRetry}
                >
                    Retry
                </button>
            </div>
        </div>
    );
}