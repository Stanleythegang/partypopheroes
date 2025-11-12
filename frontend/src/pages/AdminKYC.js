import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { useToast } from '../hooks/use-toast';
import { CheckCircle, XCircle, Eye, Download, FileText, LogOut } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminKYC = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null);
  const [reviewModal, setReviewModal] = useState(false);
  const [reviewData, setReviewData] = useState({
    action: '',
    notes: '',
    rejection_reason: ''
  });
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    loadApplications();
    loadStats();
  }, [isAdmin]);

  const loadApplications = async (status = null) => {
    try {
      setLoading(true);
      const url = status ? `${API}/kyc/applications?status_filter=${status}` : `${API}/kyc/applications`;
      const response = await axios.get(url);
      setApplications(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load KYC applications",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/kyc/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleReview = async () => {
    if (!reviewData.action) return;
    
    if (reviewData.action === 'reject' && !reviewData.rejection_reason) {
      toast({
        title: "Missing Information",
        description: "Please provide a rejection reason",
        variant: "destructive"
      });
      return;
    }

    setProcessing(true);
    try {
      await axios.post(`${API}/kyc/review/${selectedApp.id}`, reviewData);
      
      toast({
        title: "Review Submitted",
        description: `KYC application ${reviewData.action}d successfully`
      });
      
      setReviewModal(false);
      setSelectedApp(null);
      setReviewData({ action: '', notes: '', rejection_reason: '' });
      loadApplications();
      loadStats();
    } catch (error) {
      toast({
        title: "Review Failed",
        description: error.response?.data?.detail || "Something went wrong",
        variant: "destructive"
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleDownload = async (kycId, documentType, filename) => {
    try {
      const response = await axios.get(
        `${API}/kyc/download/${kycId}/${documentType}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: "Download Started",
        description: "Document is being downloaded"
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to download document",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      under_review: 'bg-blue-100 text-blue-800'
    };
    
    return (
      <Badge className={variants[status] || ''}>
        {status}
      </Badge>
    );
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Admin KYC Dashboard</h1>
            <p className="text-sm text-gray-600">Review and manage seller verifications</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              Dashboard
            </Button>
            <Button variant="outline" onClick={async () => { await logout(); navigate('/login'); }}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid md:grid-cols-5 gap-4 mb-8">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => loadApplications()}>
              <CardHeader className="pb-3">
                <CardDescription>Total Applications</CardDescription>
                <CardTitle className="text-3xl">{stats.total}</CardTitle>
              </CardHeader>
            </Card>
            <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => loadApplications('pending')}>
              <CardHeader className="pb-3">
                <CardDescription>Pending</CardDescription>
                <CardTitle className="text-3xl text-yellow-600">{stats.pending}</CardTitle>
              </CardHeader>
            </Card>
            <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => loadApplications('under_review')}>
              <CardHeader className="pb-3">
                <CardDescription>Under Review</CardDescription>
                <CardTitle className="text-3xl text-blue-600">{stats.under_review}</CardTitle>
              </CardHeader>
            </Card>
            <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => loadApplications('approved')}>
              <CardHeader className="pb-3">
                <CardDescription>Approved</CardDescription>
                <CardTitle className="text-3xl text-green-600">{stats.approved}</CardTitle>
              </CardHeader>
            </Card>
            <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => loadApplications('rejected')}>
              <CardHeader className="pb-3">
                <CardDescription>Rejected</CardDescription>
                <CardTitle className="text-3xl text-red-600">{stats.rejected}</CardTitle>
              </CardHeader>
            </Card>
          </div>
        )}

        {/* Applications List */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>KYC Applications</CardTitle>
                <CardDescription>{applications.length} applications</CardDescription>
              </div>
              <Button variant="outline" onClick={() => loadApplications()}>
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : applications.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No applications found
              </div>
            ) : (
              <div className="space-y-4">
                {applications.map((app) => (
                  <div key={app.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-lg">{app.business_name}</h3>
                          {getStatusBadge(app.status)}
                        </div>
                        <div className="grid md:grid-cols-2 gap-2 text-sm text-gray-600">
                          <p><strong>Type:</strong> {app.business_type}</p>
                          <p><strong>Submitted:</strong> {new Date(app.submitted_at).toLocaleDateString()}</p>
                        </div>
                        {app.review_notes && (
                          <p className="text-sm text-gray-600 mt-2">
                            <strong>Notes:</strong> {app.review_notes}
                          </p>
                        )}
                        {app.rejection_reason && (
                          <p className="text-sm text-red-600 mt-2">
                            <strong>Rejection:</strong> {app.rejection_reason}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedApp(app)}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        {app.status === 'pending' && (
                          <Button
                            size="sm"
                            onClick={() => {
                              setSelectedApp(app);
                              setReviewModal(true);
                            }}
                          >
                            Review
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* View Details Modal */}
      {selectedApp && !reviewModal && (
        <Dialog open={!!selectedApp} onOpenChange={() => setSelectedApp(null)}>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>KYC Application Details</DialogTitle>
              <DialogDescription>Application ID: {selectedApp.id}</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Business Name</p>
                  <p className="font-medium">{selectedApp.business_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Business Type</p>
                  <p className="font-medium capitalize">{selectedApp.business_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  {getStatusBadge(selectedApp.status)}
                </div>
                <div>
                  <p className="text-sm text-gray-600">Submitted</p>
                  <p className="font-medium">{new Date(selectedApp.submitted_at).toLocaleString()}</p>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Documents</h4>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    className="w-full justify-between"
                    onClick={() => handleDownload(selectedApp.id, 'id_document', 'id_document')}
                  >
                    <span className="flex items-center">
                      <FileText className="w-4 h-4 mr-2" />
                      ID Document
                    </span>
                    <Download className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-between"
                    onClick={() => handleDownload(selectedApp.id, 'business_document', 'business_document')}
                  >
                    <span className="flex items-center">
                      <FileText className="w-4 h-4 mr-2" />
                      Business Document
                    </span>
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {selectedApp.status === 'pending' && (
                <Button
                  className="w-full"
                  onClick={() => setReviewModal(true)}
                >
                  Review Application
                </Button>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Review Modal */}
      {reviewModal && selectedApp && (
        <Dialog open={reviewModal} onOpenChange={setReviewModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Review KYC Application</DialogTitle>
              <DialogDescription>
                {selectedApp.business_name}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Button
                  variant={reviewData.action === 'approve' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => setReviewData({ ...reviewData, action: 'approve' })}
                >
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Approve
                </Button>
                <Button
                  variant={reviewData.action === 'reject' ? 'destructive' : 'outline'}
                  className="flex-1"
                  onClick={() => setReviewData({ ...reviewData, action: 'reject' })}
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  Reject
                </Button>
              </div>

              {reviewData.action === 'reject' && (
                <div>
                  <Label htmlFor="rejection_reason">Rejection Reason *</Label>
                  <Textarea
                    id="rejection_reason"
                    placeholder="Provide a reason for rejection..."
                    value={reviewData.rejection_reason}
                    onChange={(e) => setReviewData({ ...reviewData, rejection_reason: e.target.value })}
                    rows={3}
                  />
                </div>
              )}

              <div>
                <Label htmlFor="notes">Additional Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Any additional notes..."
                  value={reviewData.notes}
                  onChange={(e) => setReviewData({ ...reviewData, notes: e.target.value })}
                  rows={3}
                />
              </div>

              <Button
                className="w-full"
                onClick={handleReview}
                disabled={!reviewData.action || processing}
              >
                {processing ? 'Processing...' : 'Submit Review'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default AdminKYC;
