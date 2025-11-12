import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Package, CheckCircle, TrendingUp, AlertCircle } from 'lucide-react';
import SellerLayout from '../../components/SellerLayout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SellerDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/products/analytics/seller-stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Products',
      value: stats?.total_products || 0,
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20'
    },
    {
      title: 'Published',
      value: stats?.published_products || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20'
    },
    {
      title: 'Approved',
      value: stats?.approved_products || 0,
      icon: CheckCircle,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20'
    },
    {
      title: 'Amazon Synced',
      value: stats?.synced_to_amazon || 0,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20'
    },
    {
      title: 'Total Views',
      value: stats?.total_views || 0,
      icon: TrendingUp,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/20'
    },
    {
      title: 'Total Sales',
      value: stats?.total_sales || 0,
      icon: TrendingUp,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100 dark:bg-pink-900/20'
    }
  ];

  if (loading) {
    return (
      <SellerLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </SellerLayout>
    );
  }

  return (
    <SellerLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Welcome back! Here's your overview</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </CardTitle>
                  <div className={`${stat.bgColor} p-2 rounded-lg`}>
                    <Icon className={`w-5 h-5 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Categories */}
        {stats?.products_by_category && stats.products_by_category.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Products by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.products_by_category.map((cat, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="font-medium capitalize">{cat.category}</span>
                    <span className="text-gray-600 dark:text-gray-400">{cat.count} products</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <a
                href="/seller/products/add"
                className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              >
                <Package className="w-6 h-6 text-blue-600" />
                <div>
                  <div className="font-medium">Add New Product</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Create a new listing</div>
                </div>
              </a>
              <a
                href="/seller/analytics"
                className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
              >
                <TrendingUp className="w-6 h-6 text-green-600" />
                <div>
                  <div className="font-medium">View Analytics</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Check your performance</div>
                </div>
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Pending Items Alert */}
        {stats && (stats.total_products - stats.approved_products) > 0 && (
          <Card className="border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20">
            <CardContent className="flex items-center gap-3 p-4">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <div>
                <div className="font-medium text-yellow-900 dark:text-yellow-200">
                  You have {stats.total_products - stats.approved_products} products pending approval
                </div>
                <div className="text-sm text-yellow-700 dark:text-yellow-300">
                  Products need admin approval before they can be synced to Amazon
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </SellerLayout>
  );
};

export default SellerDashboard;
