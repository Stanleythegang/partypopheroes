import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyEmail } = useAuth();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      handleVerification(token);
    } else {
      setStatus('error');
      setMessage('No verification token provided');
    }
  }, [searchParams]);

  const handleVerification = async (token) => {
    try {
      await verifyEmail(token);
      setStatus('success');
      setMessage('Your email has been verified successfully!');
    } catch (error) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Verification failed. The link may have expired.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          {status === 'verifying' && <Loader2 className="w-16 h-16 mx-auto animate-spin text-blue-600" />}
          {status === 'success' && <CheckCircle className="w-16 h-16 mx-auto text-green-600" />}
          {status === 'error' && <XCircle className="w-16 h-16 mx-auto text-red-600" />}
          
          <CardTitle className="mt-4">
            {status === 'verifying' && 'Verifying Email...'}
            {status === 'success' && 'Email Verified!'}
            {status === 'error' && 'Verification Failed'}
          </CardTitle>
          <CardDescription>{message}</CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          {status === 'success' && (
            <Button onClick={() => navigate('/login')} className="w-full">
              Go to Login
            </Button>
          )}
          {status === 'error' && (
            <Button onClick={() => navigate('/register')} variant="outline" className="w-full">
              Back to Register
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default VerifyEmail;
