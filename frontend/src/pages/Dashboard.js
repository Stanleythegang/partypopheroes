import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { CheckCircle, XCircle, Phone, Mail, LogOut, Upload } from 'lucide-react';

const Dashboard = () => {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, loading, navigate]);

  if (loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Hamro Dashboard</h1>
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-6">
          {/* User Profile Card */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Full Name</p>
                <p className="font-medium">{user.full_name}</p>
              </div>
              
              <div>
                <p className="text-sm text-gray-600 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </p>
                <div className="flex items-center gap-2">
                  <p className="font-medium">{user.email}</p>
                  {user.is_verified ? (
                    <Badge variant="success" className="bg-green-100 text-green-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Verified
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="w-3 h-3 mr-1" />
                      Not Verified
                    </Badge>
                  )}
                </div>
              </div>

              {user.phone && (
                <div>
                  <p className="text-sm text-gray-600 flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    Phone
                  </p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{user.phone}</p>
                    {user.phone_verified ? (
                      <Badge variant="success" className="bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Verified
                      </Badge>
                    ) : (
                      <Badge variant="outline">
                        Not Verified
                      </Badge>
                    )}
                  </div>
                </div>
              )}

              <div>
                <p className="text-sm text-gray-600">Role</p>
                <Badge className="bg-blue-100 text-blue-800 capitalize">
                  {user.role}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Action Cards */}
          <div className="space-y-6">
            {/* Phone Verification */}
            {!user.phone_verified && user.phone && (
              <Card>
                <CardHeader>
                  <CardTitle>Verify Phone Number</CardTitle>
                  <CardDescription>
                    Complete phone verification to unlock all features
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={() => navigate('/verify-phone')}
                    className="w-full"
                  >
                    <Phone className="w-4 h-4 mr-2" />
                    Verify Phone
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* KYC Card */}
            {user.role === 'seller' && (
              <Card>
                <CardHeader>
                  <CardTitle>Seller Verification (KYC)</CardTitle>
                  <CardDescription>
                    Complete KYC to start selling on Hamro
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={() => navigate('/kyc')}
                    className="w-full"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Submit KYC Documents
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Admin Panel */}
            {user.role === 'admin' && (
              <Card>
                <CardHeader>
                  <CardTitle>Admin Panel</CardTitle>
                  <CardDescription>
                    Manage KYC applications and users
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={() => navigate('/admin/kyc')}
                    className="w-full"
                  >
                    Review KYC Applications
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
