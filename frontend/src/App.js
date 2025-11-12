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

// Import seller pages
import SellerDashboard from "./pages/seller/SellerDashboard";
import ProductsList from "./pages/seller/ProductsList";
import AddProduct from "./pages/seller/AddProduct";
import EditProduct from "./pages/seller/EditProduct";
import Analytics from "./pages/seller/Analytics";
import Orders from "./pages/seller/Orders";
import Settings from "./pages/seller/Settings";
import AdminProducts from "./pages/seller/AdminProducts";
import Payouts from "./pages/seller/Payouts";

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
            
            {/* Seller Routes */}
            <Route path="/seller/dashboard" element={<SellerDashboard />} />
            <Route path="/seller/products" element={<ProductsList />} />
            <Route path="/seller/products/add" element={<AddProduct />} />
            <Route path="/seller/products/edit/:id" element={<EditProduct />} />
            <Route path="/seller/analytics" element={<Analytics />} />
            <Route path="/seller/orders" element={<Orders />} />
            <Route path="/seller/settings" element={<Settings />} />
            <Route path="/seller/admin/products" element={<AdminProducts />} />
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
