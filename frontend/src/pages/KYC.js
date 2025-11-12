import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../hooks/use-toast';
import { Upload, FileText, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const KYC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [existingKYC, setExistingKYC] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_name: '',
    business_type: 'individual',
    tax_id: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: ''
  });
  const [files, setFiles] = useState({
    id_document: null,
    business_document: null,
    additional_documents: []
  });

  useEffect(() => {
    checkExistingKYC();
  }, []);

  const checkExistingKYC = async () => {
    try {
      const response = await axios.get(`${API}/kyc/my-application`);
      setExistingKYC(response.data);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error checking KYC:', error);
      }
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e, field) => {
    const file = e.target.files[0];
    if (file) {
      setFiles({ ...files, [field]: file });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!files.id_document || !files.business_document) {
      toast({
        title: "Missing Documents",
        description: "Please upload both ID and business documents",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    try {
      const formDataToSend = new FormData();
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        formDataToSend.append(key, formData[key]);
      });
      
      // Add files
      formDataToSend.append('id_document', files.id_document);
      formDataToSend.append('business_document', files.business_document);
      
      await axios.post(`${API}/kyc/apply`, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      toast({
        title: "KYC Submitted!",
        description: "Your application is under review. We'll notify you once it's processed."
      });
      
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Submission Failed",
        description: error.response?.data?.detail || "Something went wrong",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  if (existingKYC) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
        <div className="container max-w-2xl mx-auto py-8">
          <Card>
            <CardHeader>
              <CardTitle>KYC Application Status</CardTitle>
              <CardDescription>Your seller verification application</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div>
                    <p className="font-semibold">Status</p>
                    <p className="text-2xl capitalize font-bold text-blue-600">{existingKYC.status}</p>
                  </div>
                  {existingKYC.status === 'approved' && <CheckCircle className="w-12 h-12 text-green-600" />}
                </div>

                <div>
                  <p className="text-sm text-gray-600">Business Name</p>
                  <p className="font-medium">{existingKYC.business_name}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Business Type</p>
                  <p className="font-medium capitalize">{existingKYC.business_type}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Submitted At</p>
                  <p className="font-medium">{new Date(existingKYC.submitted_at).toLocaleString()}</p>
                </div>

                {existingKYC.review_notes && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Review Notes</p>
                    <p className="font-medium">{existingKYC.review_notes}</p>
                  </div>
                )}

                {existingKYC.rejection_reason && (
                  <div className="p-4 bg-red-50 rounded-lg">
                    <p className="text-sm text-red-600">Rejection Reason</p>
                    <p className="font-medium text-red-800">{existingKYC.rejection_reason}</p>
                  </div>
                )}

                <Button onClick={() => navigate('/dashboard')} className="w-full">
                  Back to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <div className="container max-w-2xl mx-auto py-8">
        <Card>
          <CardHeader>
            <CardTitle>Seller KYC Application</CardTitle>
            <CardDescription>
              Complete this form to become a verified seller on Hamro
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Business Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Business Information</h3>
                
                <div>
                  <Label htmlFor="business_name">Business Name *</Label>
                  <Input
                    id="business_name"
                    name="business_name"
                    value={formData.business_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="business_type">Business Type *</Label>
                  <Select 
                    value={formData.business_type} 
                    onValueChange={(value) => setFormData({...formData, business_type: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="individual">Individual</SelectItem>
                      <SelectItem value="company">Company</SelectItem>
                      <SelectItem value="partnership">Partnership</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="tax_id">Tax ID (Optional)</Label>
                  <Input
                    id="tax_id"
                    name="tax_id"
                    value={formData.tax_id}
                    onChange={handleChange}
                  />
                </div>
              </div>

              {/* Address Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Address</h3>
                
                <div>
                  <Label htmlFor="address">Street Address *</Label>
                  <Input
                    id="address"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input
                      id="city"
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="state">State/Province *</Label>
                    <Input
                      id="state"
                      name="state"
                      value={formData.state}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="country">Country *</Label>
                    <Input
                      id="country"
                      name="country"
                      value={formData.country}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="postal_code">Postal Code *</Label>
                    <Input
                      id="postal_code"
                      name="postal_code"
                      value={formData.postal_code}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Document Upload */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Documents</h3>
                
                <div>
                  <Label htmlFor="id_document" className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    ID Document (PDF, JPG, PNG) *
                  </Label>
                  <Input
                    id="id_document"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFileChange(e, 'id_document')}
                    required
                    className="mt-1"
                  />
                  {files.id_document && (
                    <p className="text-sm text-green-600 mt-1">✓ {files.id_document.name}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="business_document" className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Business Document (PDF, JPG, PNG) *
                  </Label>
                  <Input
                    id="business_document"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFileChange(e, 'business_document')}
                    required
                    className="mt-1"
                  />
                  {files.business_document && (
                    <p className="text-sm text-green-600 mt-1">✓ {files.business_document.name}</p>
                  )}
                </div>

                <div className="p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>Note:</strong> All documents are encrypted before storage. 
                    Accepted formats: PDF, JPG, PNG. Max size: 10MB per file.
                  </p>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                <Upload className="w-4 h-4 mr-2" />
                {loading ? 'Submitting...' : 'Submit KYC Application'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default KYC;
