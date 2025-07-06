import React from 'react';
import { useNavigate } from 'react-router-dom';
import ProductForm from '../components/ProductForm';
import productService from '../services/productService';

const AddProductPage = () => {
    const navigate = useNavigate();

    const handleAddProduct = async (productData) => {
        try {
            // Ensure ITEMS_SOLD is a number, default to 0 if not provided or invalid
            // The ProductForm now handles this conversion, but good to be aware
            const dataToSubmit = {
                ...productData,
                ITEMS_SOLD: Number(productData.ITEMS_SOLD) || 0
            };

            await productService.createProduct(dataToSubmit);
            alert('Product added successfully!');
            navigate('/products'); // Redirect to products list after adding
        } catch (error) {
            console.error("Failed to add product:", error);
            alert('Failed to add product: ' + (error.error || error.message || 'Unknown error'));
        }
    };

    return (
        <div className="add-product-page">
            <h2>Add New Product</h2>
            <ProductForm onSubmit={handleAddProduct} isEditMode={false} />
        </div>
    );
};

export default AddProductPage;
