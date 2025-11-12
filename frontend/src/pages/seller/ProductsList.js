import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { useToast } from '../../hooks/use-toast';
import { Plus, Edit, Trash2, Eye, CheckCircle, XCircle, Package } from 'lucide-react';
import SellerLayout from '../../components/SellerLayout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProductsList = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API}/products/my-products`);
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

  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await axios.delete(`${API}/products/${productId}`);
      toast({ title: 'Success', description: 'Product deleted successfully' });
      loadProducts();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete product',
        variant: 'destructive'
      });
    }
  };

  const handleSync = async (productId) => {
    try {
      await axios.post(`${API}/products/sync/amazon`, { product_id: productId });
      toast({ title: 'Success', description: 'Product synced to Amazon!' });
      loadProducts();
    } catch (error) {
      toast({
        title: 'Sync Failed',
        description: error.response?.data?.detail || 'Failed to sync',
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

  return (
    <SellerLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Products</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{products.length} total products</p>
          </div>
          <Button onClick={() => navigate('/seller/products/add')}>
            <Plus className="w-4 h-4 mr-2" />
            Add Product
          </Button>
        </div>

        {products.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="w-16 h-16 text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-600 mb-2">No products yet</p>
              <p className="text-gray-500 mb-4">Start by creating your first product</p>
              <Button onClick={() => navigate('/seller/products/add')}>
                <Plus className="w-4 h-4 mr-2" />
                Add Product
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {products.map((product) => (
              <Card key={product.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex gap-6">
                    {/* Product Image */}
                    <div className="w-32 h-32 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                      {product.images?.[0]?.url ? (
                        <img src={product.images[0].url} alt={product.title} className="w-full h-full object-cover rounded-lg" />
                      ) : (
                        <Package className="w-12 h-12 text-gray-400" />
                      )}
                    </div>

                    {/* Product Info */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-xl font-bold">{product.title}</h3>
                          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">{product.category}</p>
                        </div>
                        <div className="text-2xl font-bold text-blue-600">${product.price}</div>
                      </div>

                      <p className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-2">{product.description}</p>

                      <div className="flex items-center gap-3 mb-4">
                        <Badge variant={product.is_published ? 'default' : 'secondary'}>
                          {product.is_published ? 'Published' : 'Draft'}
                        </Badge>
                        <Badge variant={product.is_approved ? 'success' : 'warning'} className={product.is_approved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                          {product.is_approved ? 'Approved' : 'Pending'}
                        </Badge>
                        {product.synced_to_amazon && (
                          <Badge className="bg-orange-100 text-orange-800">
                            Amazon: {product.amazon_asin}
                          </Badge>
                        )}
                        <span className="text-sm text-gray-500">Stock: {product.quantity}</span>
                        <span className="text-sm text-gray-500">
                          <Eye className="w-4 h-4 inline mr-1" />
                          {product.views} views
                        </span>
                      </div>

                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => navigate(`/seller/products/edit/${product.id}`)}>
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleDelete(product.id)}>
                          <Trash2 className="w-4 h-4 mr-1" />
                          Delete
                        </Button>
                        {product.is_approved && product.is_published && !product.synced_to_amazon && (
                          <Button size="sm" onClick={() => handleSync(product.id)}>
                            Sync to Amazon
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </SellerLayout>
  );
};

export default ProductsList;
