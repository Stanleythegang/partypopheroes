import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "./components/ui/toaster";

// Import pages
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import VerifyEmail from "./pages/VerifyEmail";
import VerifyPhone from "./pages/VerifyPhone";
import Dashboard from "./pages/Dashboard";
import KYC from "./pages/KYC";
import AdminKYC from "./pages/AdminKYC";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/verify-phone" element={<VerifyPhone />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/kyc" element={<KYC />} />
            <Route path="/admin/kyc" element={<AdminKYC />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
