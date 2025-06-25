import { useNavigate } from "react-router-dom";
import { useUser } from "../context/UserContext";
import styles from "./MainPage.module.css";

export default function MainPage() {
    const navigate = useNavigate();
    const { user, setUser } = useUser();

    const handleLogout = () => {
        setUser(null);
        navigate("/login");
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                저기어때 – AI 여행 가이드
                {user && (
                    <>
                        <span className={styles.username}>👤 {user.name}</span>
                        <button onClick={handleLogout} className={styles.logoutButton}>
                            로그아웃
                        </button>
                    </>
                )}
            </div>

            <h1 className={styles.title}>
                Welcome to <span className={styles.brand}>저기어때!</span>
            </h1>
            <p className={styles.subtitle}>
                편리한 AI 일정생성으로 저기어때와 여행을 떠나보아요!
            </p>

            <div className={styles.buttonGroup}>
                <button className={styles.button} onClick={() => navigate("/input")}>일정 생성 하기</button>
                <button className={styles.button} onClick={() => navigate("/saved")}>저장된 일정 불러오기</button>
            </div>
        </div>
    );
}