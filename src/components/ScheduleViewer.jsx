// src/components/ScheduleViewer.jsx
import React from 'react';
import styles from './ScheduleViewer.module.css';

export default function ScheduleViewer({ places, segments = [], planId }) {
    if (!places || places.length === 0) {
        return <p className="text-gray-500">📭 일정이 비어있습니다.</p>;
    }

    const handleDownload = () => {
        const url = `http://localhost:8000/api/download_plan_pdf?plan_id=${planId}`;
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'travel_plan.pdf');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div>
            <ul className={styles.list}>
                {places.map((place, index) => (
                    <React.Fragment key={index}>
                        <li className={styles.item}>
                            <div className={styles.name}>📍 {place.name}</div>
                            <div className={styles.detail}>
                                위도: {place.location.latitude}, 경도: {place.location.longitude}
                            </div>
                            <div className={styles.concepts}>
                                🧭 {place.concept?.join(', ') || 'N/A'}
                            </div>
                        </li>
                        {segments && index < segments.length && (
                            <li className={styles.segment}>
                                🚶 다음 장소까지 {segments[index]?.distance?.toFixed(2)} km 이동 (
                                {segments[index]?.duration?.toFixed(0)}분)
                            </li>
                        )}
                    </React.Fragment>
                ))}
            </ul>
        </div>
    );
}