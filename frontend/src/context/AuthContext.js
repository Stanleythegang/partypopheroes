import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));

  // Axios interceptor for adding token to requests
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        if (accessToken && config.url.startsWith(API)) {
          config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => axios.interceptors.request.eject(interceptor);
  }, [accessToken]);

  // Load user on mount
  useEffect(() => {
    if (accessToken) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user:', error);
      if (error.response?.status === 401) {
        // Try to refresh token
        await refreshTokens();
      } else {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { access_token, refresh_token } = response.data;
    
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    setAccessToken(access_token);
    setRefreshToken(refresh_token);
    
    await loadUser();
    return response.data;
  };

  const register = async (email, password, full_name, phone) => {
    const response = await axios.post(`${API}/auth/register`, {
      email,
      password,
      full_name,
      phone
    });
    return response.data;
  };

  const logout = async () => {
    try {
      if (refreshToken) {
        await axios.post(`${API}/auth/logout`, { refresh_token: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setAccessToken(null);
      setRefreshToken(null);
      setUser(null);
    }
  };

  const refreshTokens = async () => {
    try {
      const response = await axios.post(`${API}/auth/refresh`, {
        refresh_token: refreshToken
      });
      const { access_token, refresh_token: new_refresh_token } = response.data;
      
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', new_refresh_token);
      setAccessToken(access_token);
      setRefreshToken(new_refresh_token);
      
      await loadUser();
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return false;
    }
  };

  const verifyEmail = async (token) => {
    const response = await axios.post(`${API}/auth/verify-email`, { token });
    return response.data;
  };

  const sendOTP = async (phone) => {
    const response = await axios.post(
      `${API}/auth/send-otp`,
      { phone },
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    return response.data;
  };

  const verifyOTP = async (phone, otp) => {
    const response = await axios.post(
      `${API}/auth/verify-otp`,
      { phone, otp },
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    await loadUser();
    return response.data;
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    verifyEmail,
    sendOTP,
    verifyOTP,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isSeller: user?.role === 'seller'
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
