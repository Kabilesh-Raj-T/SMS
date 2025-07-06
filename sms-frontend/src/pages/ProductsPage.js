import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom'; // For "Add Product" link
import productService from '../services/productService';
import './ProductsPage.css'; // We'll create this for styling

const ProductsPage = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                setLoading(true);
                const data = await productService.getAllProducts();
                setProducts(data);
                setError(null);
            } catch (err) {
                setError(err.message || 'Failed to fetch products');
                setProducts([]); // Clear products on error
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    const handleDeleteProduct = async (productId) => {
        // Basic confirmation before deleting
        if (window.confirm('Are you sure you want to delete this product?')) {
            try {
                await productService.deleteProduct(productId);
                setProducts(products.filter(p => p.ID !== productId)); // Update UI
                alert('Product deleted successfully!');
            } catch (err) {
                alert('Failed to delete product: ' + (err.error || err.message));
            }
        }
    };

    if (loading) {
        return <p>Loading products...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    return (
        <div className="products-page">
            <h1>Products Management</h1>
            <Link to="/products/add" className="btn btn-primary add-product-link">Add New Product</Link>

            {products.length === 0 ? (
                <p>No products found.</p>
            ) : (
                <table className="products-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Brand</th>
                            <th>Price</th>
                            <th>Quantity</th>
                            <th>Sold</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map(product => (
                            <tr key={product.ID}>
                                <td>{product.ID}</td>
                                <td>{product.NAME}</td>
                                <td>{product.BRAND}</td>
                                <td>${product.SELLING_PRICE ? product.SELLING_PRICE.toFixed(2) : 'N/A'}</td>
                                <td>{product.QUANTITY}</td>
                                <td>{product.ITEMS_SOLD}</td>
                                <td className="product-actions">
                                    <Link to={`/products/edit/${product.ID}`} className="btn btn-secondary btn-sm">Edit</Link>
                                    {/* <button onClick={() => alert(`View details for ${product.NAME}`)} className="btn btn-info btn-sm">View</button> */}
                                    <button onClick={() => handleDeleteProduct(product.ID)} className="btn btn-danger btn-sm">Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default ProductsPage;
