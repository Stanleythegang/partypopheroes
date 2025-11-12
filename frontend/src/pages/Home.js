import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { CheckCircle, ArrowRight, Shield, Zap, Users } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    try {
      const response = await axios.get(`${API}/`);
      setApiStatus(response.data);
    } catch (e) {
      console.error("API connection error:", e);
      setApiStatus({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Hamro
            </h1>
            {apiStatus && !apiStatus.error && (
              <Badge variant="success" className="bg-green-100 text-green-800">
                <CheckCircle className="w-3 h-3 mr-1" />
                v{apiStatus.version}
              </Badge>
            )}
          </div>
          <div className="flex gap-2">
            {isAuthenticated ? (
              <>
                <Button variant="outline" onClick={() => navigate('/dashboard')}>
                  Dashboard
                </Button>
                {user?.role === 'admin' && (
                  <Button variant="outline" onClick={() => navigate('/admin/kyc')}>
                    Admin
                  </Button>
                )}
              </>
            ) : (
              <>
                <Button variant="outline" onClick={() => navigate('/login')}>
                  Login
                </Button>
                <Button onClick={() => navigate('/register')}>
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Welcome to Hamro Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Complete authentication and seller onboarding system with KYC verification
          </p>
          
          {loading ? (
            <div className="text-lg text-gray-500">Connecting to backend...</div>
          ) : apiStatus?.error ? (
            <Card className="max-w-2xl mx-auto mb-8">
              <CardContent className="pt-6">
                <div className="text-red-600">Error: {apiStatus.error}</div>
              </CardContent>
            </Card>
          ) : (
            <Card className="max-w-2xl mx-auto mb-8">
              <CardContent className="pt-6">
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Backend Connected - {apiStatus?.message}</span>
                </div>
                {apiStatus?.features && (
                  <div className="mt-4 flex flex-wrap gap-2 justify-center">
                    {apiStatus.features.map((feature) => (
                      <Badge key={feature} className="capitalize">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          <div className="flex gap-4 justify-center">
            {!isAuthenticated && (
              <>
                <Button size="lg" onClick={() => navigate('/register')} className="gap-2">
                  Get Started
                  <ArrowRight className="w-4 h-4" />
                </Button>
                <Button size="lg" variant="outline" onClick={() => navigate('/login')}>
                  Sign In
                </Button>
              </>
            )}
            {isAuthenticated && (
              <Button size="lg" onClick={() => navigate('/dashboard')} className="gap-2">
                Go to Dashboard
                <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-4xl font-bold text-center mb-12">Platform Features</h2>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Shield className="w-12 h-12 text-blue-600 mb-4" />
              <CardTitle>Secure Authentication</CardTitle>
              <CardDescription>
                Complete authentication system with email & phone verification
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  JWT + Refresh Tokens
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Email Verification
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Phone OTP Verification
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Password Hashing (bcrypt)
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Users className="w-12 h-12 text-purple-600 mb-4" />
              <CardTitle>Seller Onboarding</CardTitle>
              <CardDescription>
                Complete KYC verification system for sellers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Document Upload
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Encrypted Storage
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Admin Review Panel
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Status Tracking
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Zap className="w-12 h-12 text-orange-600 mb-4" />
              <CardTitle>Modern Stack</CardTitle>
              <CardDescription>
                Built with cutting-edge technologies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  React 19 + React Router
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  FastAPI (Python)
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  MongoDB Database
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Tailwind + Shadcn UI
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      {!isAuthenticated && (
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Create your account today and join our marketplace
            </p>
            <Button 
              size="lg" 
              variant="secondary"
              onClick={() => navigate('/register')}
              className="gap-2"
            >
              Create Account
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="bg-white border-t">
        <div className="container mx-auto px-4 py-8 text-center text-gray-600">
          <p className="mb-2">
            Built with ❤️ on Emergent Platform
          </p>
          <p className="text-sm">
            React + FastAPI + MongoDB • JWT Auth • KYC Verification • Encrypted Storage
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;
