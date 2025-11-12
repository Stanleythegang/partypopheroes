import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { useToast } from '../../hooks/use-toast';
import { CheckCircle, XCircle, Package } from 'lucide-react';
import SellerLayout from '../../components/SellerLayout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminProducts = () => {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!isAdmin) {
      navigate('/seller/dashboard');
      return;
    }
    loadProducts();
  }, [filter]);

  const loadProducts = async () => {
    try {
      const url = filter === 'all' 
        ? `${API}/products/admin/all`
        : `${API}/products/admin/all?is_approved=${filter === 'approved'}`;
      const response = await axios.get(url);
      setProducts(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load products',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (productId, action) => {
    try {
      await axios.post(`${API}/products/admin/${productId}/approve`, {
        action: action,
        notes: `Product ${action}d by admin`
      });
      toast({ 
        title: 'Success', 
        description: `Product ${action}d successfully!` 
      });
      loadProducts();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Action failed',
        variant: 'destructive'
      });
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

  const pendingProducts = products.filter(p => !p.is_approved);
  const approvedProducts = products.filter(p => p.is_approved);

  return (
    <SellerLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Admin: Product Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Review and approve seller products</p>
        </div>

        <Tabs value={filter} onValueChange={setFilter}>
          <TabsList>
            <TabsTrigger value="all">All ({products.length})</TabsTrigger>
            <TabsTrigger value="pending">Pending ({pendingProducts.length})</TabsTrigger>
            <TabsTrigger value="approved">Approved ({approvedProducts.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            <ProductsGrid products={products} onApprove={handleApprove} />
          </TabsContent>

          <TabsContent value="pending" className="mt-6">
            <ProductsGrid products={pendingProducts} onApprove={handleApprove} />
          </TabsContent>

          <TabsContent value="approved" className="mt-6">
            <ProductsGrid products={approvedProducts} onApprove={handleApprove} />
          </TabsContent>
        </Tabs>
      </div>
    </SellerLayout>
  );
};

const ProductsGrid = ({ products, onApprove }) => {
  if (products.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Package className="w-16 h-16 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-600">No products found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-6">
      {products.map((product) => (
        <Card key={product.id}>
          <CardContent className="p-6">
            <div className="flex gap-6">
              <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                {product.images?.[0]?.url ? (
                  <img src={product.images[0].url} alt={product.title} className="w-full h-full object-cover rounded-lg" />
                ) : (
                  <Package className="w-8 h-8 text-gray-400" />
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="text-lg font-bold">{product.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">by {product.seller_name}</p>
                  </div>
                  <div className="text-xl font-bold text-blue-600">${product.price}</div>
                </div>

                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3 line-clamp-2">{product.description}</p>

                <div className="flex items-center gap-3 mb-4">
                  <Badge>{product.category}</Badge>
                  <Badge variant={product.is_published ? 'default' : 'secondary'}>
                    {product.is_published ? 'Published' : 'Draft'}
                  </Badge>
                  <Badge variant={product.is_approved ? 'success' : 'warning'} className={product.is_approved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                    {product.is_approved ? 'Approved' : 'Pending'}
                  </Badge>
                  {product.synced_to_amazon && (
                    <Badge className="bg-orange-100 text-orange-800">Amazon Synced</Badge>
                  )}
                  <span className="text-sm text-gray-500">Qty: {product.quantity}</span>
                </div>

                {!product.is_approved && (
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => onApprove(product.id, 'approve')}>
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Approve
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => onApprove(product.id, 'reject')}>
                      <XCircle className="w-4 h-4 mr-1" />
                      Reject
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default AdminProducts;
