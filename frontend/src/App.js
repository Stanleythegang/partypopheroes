import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const testConnection = async () => {
    try {
      setLoading(true);
      // Test main API
      const response = await axios.get(`${API}/`);
      setApiStatus(response.data);

      // Test products API
      const productsRes = await axios.get(`${API}/products`);
      setProducts(productsRes.data);

      // Test AI recommendations
      const aiRes = await axios.post(`${API}/ai/recommendations`, {
        user_id: "test-user",
        limit: 3
      });
      setRecommendations(aiRes.data);

      console.log("✅ All API connections successful");
    } catch (e) {
      console.error("❌ API connection error:", e);
      setApiStatus({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testConnection();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Hamro Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            React + FastAPI + MongoDB Stack
          </p>
          
          {loading ? (
            <div className="text-lg text-gray-500">Connecting to backend...</div>
          ) : apiStatus ? (
            <Card className="max-w-2xl mx-auto mb-8">
              <CardHeader>
                <CardTitle className="text-2xl">✅ Backend Connected</CardTitle>
                <CardDescription>API Response</CardDescription>
              </CardHeader>
              <CardContent>
                {apiStatus.error ? (
                  <div className="text-red-600">Error: {apiStatus.error}</div>
                ) : (
                  <div className="space-y-2 text-left">
                    <p><strong>Message:</strong> {apiStatus.message}</p>
                    <p><strong>Platform:</strong> {apiStatus.platform}</p>
                    <p><strong>Version:</strong> {apiStatus.version}</p>
                    <p><strong>Status:</strong> <span className="text-green-600 font-semibold">{apiStatus.status}</span></p>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : null}
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card>
            <CardHeader>
              <CardTitle>🔐 Authentication</CardTitle>
              <CardDescription>User auth module ready</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Placeholder endpoints for register, login, and user management.
              </p>
              <Button variant="outline" className="w-full">
                /api/auth/*
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>📦 Products</CardTitle>
              <CardDescription>{products.length} products loaded</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Full CRUD operations for product management.
              </p>
              <Button variant="outline" className="w-full">
                /api/products/*
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>🤖 AI Services</CardTitle>
              <CardDescription>{recommendations.length} recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                AI-powered recommendations, search, and sentiment analysis.
              </p>
              <Button variant="outline" className="w-full">
                /api/ai/*
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Sample Products */}
        {products.length > 0 && (
          <div className="mb-12">
            <h2 className="text-3xl font-bold mb-6 text-center">Sample Products</h2>
            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {products.map((product) => (
                <Card key={product.id}>
                  <CardHeader>
                    <CardTitle>{product.name}</CardTitle>
                    <CardDescription>{product.category}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm mb-2">{product.description}</p>
                    <p className="text-2xl font-bold text-blue-600">${product.price}</p>
                    <p className="text-sm text-gray-500">Stock: {product.stock}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* AI Recommendations */}
        {recommendations.length > 0 && (
          <div className="mb-12">
            <h2 className="text-3xl font-bold mb-6 text-center">AI Recommendations</h2>
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              {recommendations.map((rec, idx) => (
                <Card key={idx}>
                  <CardHeader>
                    <CardTitle className="text-lg">{rec.product_name}</CardTitle>
                    <CardDescription>Confidence: {(rec.confidence_score * 100).toFixed(0)}%</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{rec.reason}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t">
          <p className="text-gray-600">
            Built with React + FastAPI + MongoDB on Emergent Platform
          </p>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
