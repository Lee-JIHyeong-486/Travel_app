import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../context/UserContext";
import styles from "./LoginPage.module.css";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const navigate = useNavigate();
    const { setUser } = useUser();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const result = await response.json();

            if (result.success) {
            const userId = result.user_id;
            setUser({
                id: userId,
                name: email  // 입력한 이메일을 name에 저장
            });
            navigate("/", { state: { userId } });
            } else {
                setMessage(result.message || "로그인 실패");
            }
        } catch (error) {
            console.error("Login error:", error);
            setMessage("서버 오류. 잠시 후 다시 시도해주세요.");
        }
    };

    return (
        <div className={styles.container}>
            <form onSubmit={handleSubmit} className={styles.form}>
                <h2 className={styles.heading}>로그인</h2>

                <input
                    type="email"
                    placeholder="이메일"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={styles.input}
                    required
                />
                <input
                    type="password"
                    placeholder="비밀번호"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={styles.input}
                    required
                />
                <button type="submit" className={styles.button}>
                    로그인
                </button>

                {message && <div className={styles.message}>{message}</div>}

                <div className={styles.signup}>
                    계정이 없으신가요?{" "}
                    <span className={styles.link} onClick={() => navigate("/register")}>
                        회원가입
                    </span>
                </div>
            </form>
        </div>
    );
}