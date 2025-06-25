import React from "react";

import {
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import MainPage from "./pages/MainPage";
import UserInputPage from "./pages/UserInputPage";
import MapLoadingPage from "./pages/MapLoadingPage";
import MapVisualizePage from "./pages/MapVisualizePage";
import SavePage from "./pages/SavePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import { UserProvider, useUser } from "./context/UserContext";

// 로그인된 사용자만 접근 가능한 라우트 보호 컴포넌트
function ProtectedRoute({ element }) {
    const { user } = useUser();
    return user ? element : <Navigate to="/login" replace />;
}

// 라우터 정의
function AppRoutes() {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/" element={<ProtectedRoute element={<MainPage />} />} />
            <Route path="/input" element={<ProtectedRoute element={<UserInputPage />} />} />
            <Route path="/loading" element={<ProtectedRoute element={<MapLoadingPage />} />} />
            <Route path="/map_visualize" element={<ProtectedRoute element={<MapVisualizePage />} />} />
            <Route path="/saved" element={<ProtectedRoute element={<SavePage />} />} />
        </Routes>
    );
}

// 앱 루트 컴포넌트
export default function App() {
    return (
        <UserProvider>
            <AppRoutes />
        </UserProvider>
    );
}
