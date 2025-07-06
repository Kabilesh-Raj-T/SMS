import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ProductForm from '../components/ProductForm';
import productService from '../services/productService';

const EditProductPage = () => {
    const { productId } = useParams(); // Get productId from URL
    const navigate = useNavigate();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProductDetails = async () => {
            try {
                setLoading(true);
                const data = await productService.getProductById(productId);
                setProduct(data);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch product details:", err);
                setError(err.message || `Failed to fetch product details for ID ${productId}`);
                setProduct(null);
            } finally {
                setLoading(false);
            }
        };

        if (productId) {
            fetchProductDetails();
        }
    }, [productId]);

    const handleEditProduct = async (productData) => {
        try {
            // The productData from ProductForm already has numbers converted
            // ID is not part of productData from the form if it's disabled,
            // so we use productId from URL params for the API call.
            await productService.updateProduct(productId, productData);
            alert('Product updated successfully!');
            navigate('/products'); // Redirect to products list
        } catch (error) {
            console.error("Failed to update product:", error);
            alert('Failed to update product: ' + (error.error || error.message || 'Unknown error'));
        }
    };

    if (loading) {
        return <p>Loading product details...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    if (!product) {
        return <p>Product not found.</p>; // Or a more sophisticated 404 component
    }

    return (
        <div className="edit-product-page">
            <h2>Edit Product (ID: {product.ID})</h2>
            <ProductForm onSubmit={handleEditProduct} initialData={product} isEditMode={true} />
        </div>
    );
};

export default EditProductPage;
