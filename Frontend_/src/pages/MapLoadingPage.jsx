import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './MapLoading.module.css';

export default function MapLoading() {
  const location = useLocation();
  const navigate = useNavigate();
  const userInput = location.state?.userRequest;

  console.log("this is userInput:\n", userInput)
  console.log(userInput);

  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Starting map generation...");

  useEffect(() => {
    const fetchMapData = async () => {
      try {
        setProgress(10);
        setStatus("Fetching POIs...");

        console.log(JSON.stringify(userInput));

        const getPoisRes = await fetch("http://localhost:3000/api/get_pois", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(userInput),
        });

        const poisData = await getPoisRes.json();
        const userRequest = poisData.user_request;

        setProgress(50);
        setStatus("Optimizing route...");

        const routeOptimRes = await fetch("http://localhost:3000/api/route_optim", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(userRequest),
        });

        const routeData = await routeOptimRes.json();
        const travelPlan = routeData.travel_plan;
        console.log("travel plan is :\n",travelPlan)
        setProgress(100);
        setStatus("Map ready! Redirecting...");

        setTimeout(() => {
          navigate("/map_visualize", {
            state: {
              userRequest: routeData.user_request,
              travelPlan: travelPlan,
            },
          });
        }, 1000);

      } catch (err) {
        console.error("Failed to fetch data:", err);
        alert("⚠️ Internal server error occurred. Please try again later.");
        navigate("/", { state: { userInput: userInput } });
      }
    };

    fetchMapData();
  }, [userInput, navigate]);

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>🗺️ Generating Your Travel Map</h2>
      <p className={styles.status}>{status}</p>

      <div className={styles.progressBarBackground}>
        <div
          className={styles.progressBarFill}
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
}
