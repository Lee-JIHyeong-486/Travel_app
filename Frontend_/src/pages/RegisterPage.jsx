import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./RegisterPage.module.css";

const RegisterPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch("/api/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            const result = await response.json();

            if (result.success) {
                console.log("register success!");
                navigate("/login");
            } else {
                setMessage(result.message || "회원가입 실패");
            }
        } catch (error) {
            console.error("Register error:", error);
            setMessage("서버 오류. 잠시 후 다시 시도해주세요.");
        }
    };

    return (
        <div className={styles.container}>
            <form onSubmit={handleSubmit} className={styles.form}>
                <h2 className={styles.title}>회원가입</h2>

                <input
                    type="email"
                    name="email"
                    placeholder="이메일"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={styles.input}
                />
                <input
                    type="password"
                    name="password"
                    placeholder="비밀번호"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={styles.input}
                />

                <button type="submit" className={styles.submitButton}>
                    회원가입
                </button>

                {message && <div className={styles.message}>{message}</div>}

                <div className={styles.loginPrompt}>
                    이미 계정이 있으신가요?{' '}
                    <span className={styles.loginLink} onClick={() => navigate("/login")}>
                        로그인
                    </span>
                </div>
            </form>
        </div>
    );
};

export default RegisterPage;