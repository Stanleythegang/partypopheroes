import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { useToast } from '../../hooks/use-toast';
import { DollarSign, CreditCard, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import SellerLayout from '../../components/SellerLayout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Payouts = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [accountStatus, setAccountStatus] = useState(null);
  const [balance, setBalance] = useState(null);
  const [payoutHistory, setPayoutHistory] = useState([]);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [requesting, setRequesting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadAccountStatus(),
        loadBalance(),
        loadPayoutHistory()
      ]);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAccountStatus = async () => {
    try {
      const response = await axios.get(`${API}/payouts/account/status`);
      setAccountStatus(response.data);
    } catch (error) {
      setAccountStatus({ connected: false });
    }
  };

  const loadBalance = async () => {
    try {
      const response = await axios.get(`${API}/payouts/balance`);
      setBalance(response.data);
    } catch (error) {
      console.error('Failed to load balance:', error);
    }
  };

  const loadPayoutHistory = async () => {
    try {
      const response = await axios.get(`${API}/payouts/history`);
      setPayoutHistory(response.data);
    } catch (error) {
      console.error('Failed to load payout history:', error);
    }
  };

  const createStripeAccount = async () => {
    try {
      await axios.post(`${API}/payouts/connect/account`, {
        country: 'US',
        email: 'seller@example.com',
        business_type: 'individual'
      });
      toast({ title: 'Success', description: 'Stripe account created!' });
      loadAccountStatus();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create account',
        variant: 'destructive'
      });
    }
  };

  const requestPayout = async () => {
    if (!payoutAmount || parseFloat(payoutAmount) <= 0) {
      toast({ title: 'Error', description: 'Enter valid amount', variant: 'destructive' });
      return;
    }

    setRequesting(true);
    try {
      await axios.post(`${API}/payouts/request`, {
        amount: parseFloat(payoutAmount),
        currency: 'USD',
        description: 'Seller payout request'
      });
      toast({ title: 'Success', description: 'Payout requested successfully!' });
      setPayoutAmount('');
      loadBalance();
      loadPayoutHistory();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to request payout',
        variant: 'destructive'
      });
    } finally {
      setRequesting(false);
    }
  };

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
          <h1 className="text-3xl font-bold">Payouts</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your earnings and payouts</p>
        </div>

        {/* Stripe Account Status */}
        {!accountStatus?.connected ? (
          <Card className="border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <AlertCircle className="w-12 h-12 text-blue-600" />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">Connect Stripe Account</h3>
                  <p className="text-gray-700 dark:text-gray-300 mb-3">
                    Connect your Stripe account to receive payouts from your sales.
                  </p>
                  <Button onClick={createStripeAccount}>
                    <CreditCard className="w-4 h-4 mr-2" />
                    Connect Stripe
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Balance Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Available Balance</CardTitle>
                  <DollarSign className="w-4 h-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">${balance?.available.toFixed(2) || '0.00'}</div>
                  <p className="text-xs text-gray-500 mt-1">Ready to withdraw</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Pending Balance</CardTitle>
                  <Clock className="w-4 h-4 text-yellow-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">${balance?.pending.toFixed(2) || '0.00'}</div>
                  <p className="text-xs text-gray-500 mt-1">Processing</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Account Status</CardTitle>
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <Badge className={accountStatus.payouts_enabled ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                    {accountStatus.payouts_enabled ? 'Active' : 'Pending'}
                  </Badge>
                  <p className="text-xs text-gray-500 mt-2">Payouts {accountStatus.payouts_enabled ? 'enabled' : 'disabled'}</p>
                </CardContent>
              </Card>
            </div>

            {/* Request Payout */}
            <Card>
              <CardHeader>
                <CardTitle>Request Payout</CardTitle>
                <CardDescription>Transfer available balance to your bank account</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <Label htmlFor="amount">Amount ($)</Label>
                    <Input
                      id="amount"
                      type="number"
                      step="0.01"
                      min="0"
                      max={balance?.available || 0}
                      value={payoutAmount}
                      onChange={(e) => setPayoutAmount(e.target.value)}
                      placeholder="0.00"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Max: ${balance?.available.toFixed(2) || '0.00'}
                    </p>
                  </div>
                  <div className="flex items-end">
                    <Button onClick={requestPayout} disabled={requesting || !accountStatus.payouts_enabled}>
                      {requesting ? 'Processing...' : 'Request Payout'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Payout History */}
            <Card>
              <CardHeader>
                <CardTitle>Payout History</CardTitle>
                <CardDescription>{payoutHistory.length} payouts</CardDescription>
              </CardHeader>
              <CardContent>
                {payoutHistory.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No payouts yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {payoutHistory.map((payout) => (
                      <div key={payout.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">${payout.amount.toFixed(2)}</p>
                          <p className="text-sm text-gray-600">
                            {new Date(payout.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge variant={payout.status === 'paid' ? 'success' : 'warning'} className={payout.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                          {payout.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </SellerLayout>
  );
};

export default Payouts;
