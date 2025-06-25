import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useUser } from "../context/UserContext";
import styles from "./InputForm.module.css";

export default function InputForm() {
  const navigate = useNavigate();
  const { user } = useUser();
  const UserId = user?.id || "";

  const [form, setForm] = useState({
    location: "",
    durationStart: "",
    durationEnd: "",
    companions: 1,
    concept: "",
    extra_request: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]:
        name === "companions" ? parseInt(value, 10) || 0 : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const userRequest = {
      user_id: UserId,
      location: form.location,
      duration: {
        start: form.durationStart,
        end: form.durationEnd,
      },
      companions: parseInt(form.companions, 10),
      concept: form.concept,
      extra_request: form.extra_request,
      kwargs: {
        filter: null,
        prev_map_data: null,
        cache_key: null,
      },
    };

    navigate("/loading", { state: { userRequest } });
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.title}>여행 정보 입력</h2>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="location">
            Location:
          </label>
          <select
            name="location"
            id="location"
            value={form.location}
            onChange={handleChange}
            className={styles.input}
            required
          >
            <option value="">-- Select --</option>
            <option value="New York">New York</option>
            <option value="Los Angeles">Los Angeles</option>
            <option value="Sydney">Sydney</option>
            <option value="Tokyo">Tokyo</option>
            <option value="Hongkong">Hongkong</option>
            <option value="Jeju">Jeju</option>
          </select>
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="durationStart">
            Duration Start:
          </label>
          <input
            type="date"
            id="durationStart"
            name="durationStart"
            value={form.durationStart}
            onChange={handleChange}
            className={styles.input}
            required
          />
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="durationEnd">
            Duration End:
          </label>
          <input
            type="date"
            id="durationEnd"
            name="durationEnd"
            value={form.durationEnd}
            onChange={handleChange}
            className={styles.input}
            required
          />
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="companions">
            Number of Companions:
          </label>
          <input
            type="number"
            id="companions"
            name="companions"
            min="1"
            max="10"
            value={form.companions}
            onChange={handleChange}
            className={styles.input}
            required
          />
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="concept">
            Trip Concept:
          </label>
          <select
            name="concept"
            id="concept"
            value={form.concept}
            onChange={handleChange}
            className={styles.input}
            required
          >
            <option value="">-- Select --</option>
            <option value="peaceful nature areas">🌿 Nature & Relaxation</option>
            <option value="popular local food spots">🍜 Foodie Adventure</option>
            <option value="cultural sites and heritage attractions">
              🏛️ Cultural & Historical
            </option>
            <option value="family adventure attractions">
              🎢 Active & Funion
            </option>
            <option value="scenic viewpoints for photography">
              📸 Scenic & Photogenic
            </option>
          </select>
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="extra_request">
            Extra Request:
          </label>
          <input
            type="text"
            id="extra_request"
            name="extra_request"
            value={form.extra_request}
            onChange={handleChange}
            className={styles.input}
          />
        </div>

        <button type="submit" className={styles.submitButton}>
          Submit
        </button>
      </form>
    </div>
  );
}