import React, { useState, useEffect } from 'react';
import './ProductForm.css'; // For styling the form

const ProductForm = ({ onSubmit, initialData = null, isEditMode = false }) => {
    const [product, setProduct] = useState({
        ID: '',
        NAME: '',
        SELLING_PRICE: '',
        COST_PRICE: '',
        BRAND: '',
        QUANTITY: '',
        ITEMS_SOLD: '' // Typically not set directly by user when creating, but good for edit
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (initialData) {
            // Ensure all fields are strings for controlled inputs, especially numbers
            const stringifiedData = Object.keys(initialData).reduce((acc, key) => {
                acc[key] = initialData[key] !== null && initialData[key] !== undefined ? String(initialData[key]) : '';
                return acc;
            }, {});
            setProduct(stringifiedData);
        } else {
            // Reset form if no initial data (e.g., for add mode after an edit)
            setProduct({
                ID: '', NAME: '', SELLING_PRICE: '', COST_PRICE: '',
                BRAND: '', QUANTITY: '', ITEMS_SOLD: ''
            });
        }
    }, [initialData]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setProduct(prev => ({ ...prev, [name]: value }));
        // Basic validation on change (optional)
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        if (!product.ID && !isEditMode) newErrors.ID = "Product ID is required."; // ID might be non-editable in edit mode
        if (!product.NAME) newErrors.NAME = "Product Name is required.";
        if (!product.SELLING_PRICE || isNaN(parseFloat(product.SELLING_PRICE)) || parseFloat(product.SELLING_PRICE) < 0) {
            newErrors.SELLING_PRICE = "Valid Selling Price is required (must be a non-negative number).";
        }
        if (!product.COST_PRICE || isNaN(parseFloat(product.COST_PRICE)) || parseFloat(product.COST_PRICE) < 0) {
            newErrors.COST_PRICE = "Valid Cost Price is required (must be a non-negative number).";
        }
        if (!product.BRAND) newErrors.BRAND = "Brand is required.";
        if (!product.QUANTITY || isNaN(parseInt(product.QUANTITY, 10)) || parseInt(product.QUANTITY, 10) < 0) {
            newErrors.QUANTITY = "Valid Quantity is required (must be a non-negative integer).";
        }
        // ITEMS_SOLD is usually managed by the system, but if editable, add validation.
        // For now, assume it's less critical for user input validation during add/edit.
        if (product.ITEMS_SOLD !== '' && (isNaN(parseInt(product.ITEMS_SOLD, 10)) || parseInt(product.ITEMS_SOLD, 10) < 0)) {
            newErrors.ITEMS_SOLD = "Items Sold must be a non-negative integer if provided.";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (validateForm()) {
            // Convert numeric fields from string back to number before submitting
            const productDataToSubmit = {
                ...product,
                SELLING_PRICE: parseFloat(product.SELLING_PRICE),
                COST_PRICE: parseFloat(product.COST_PRICE),
                QUANTITY: parseInt(product.QUANTITY, 10),
                ITEMS_SOLD: product.ITEMS_SOLD === '' ? 0 : parseInt(product.ITEMS_SOLD, 10) // Default to 0 if empty
            };
            onSubmit(productDataToSubmit);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="product-form">
            <div className="form-group">
                <label htmlFor="ID">Product ID</label>
                <input
                    type="text"
                    name="ID"
                    id="ID"
                    value={product.ID}
                    onChange={handleChange}
                    disabled={isEditMode} // ID is usually not editable
                />
                {errors.ID && <p className="error-text">{errors.ID}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="NAME">Product Name</label>
                <input
                    type="text"
                    name="NAME"
                    id="NAME"
                    value={product.NAME}
                    onChange={handleChange}
                />
                {errors.NAME && <p className="error-text">{errors.NAME}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="BRAND">Brand</label>
                <input
                    type="text"
                    name="BRAND"
                    id="BRAND"
                    value={product.BRAND}
                    onChange={handleChange}
                />
                {errors.BRAND && <p className="error-text">{errors.BRAND}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="SELLING_PRICE">Selling Price</label>
                <input
                    type="number"
                    name="SELLING_PRICE"
                    id="SELLING_PRICE"
                    value={product.SELLING_PRICE}
                    onChange={handleChange}
                    step="0.01"
                />
                {errors.SELLING_PRICE && <p className="error-text">{errors.SELLING_PRICE}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="COST_PRICE">Cost Price</label>
                <input
                    type="number"
                    name="COST_PRICE"
                    id="COST_PRICE"
                    value={product.COST_PRICE}
                    onChange={handleChange}
                    step="0.01"
                />
                {errors.COST_PRICE && <p className="error-text">{errors.COST_PRICE}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="QUANTITY">Quantity</label>
                <input
                    type="number"
                    name="QUANTITY"
                    id="QUANTITY"
                    value={product.QUANTITY}
                    onChange={handleChange}
                    step="1"
                />
                {errors.QUANTITY && <p className="error-text">{errors.QUANTITY}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="ITEMS_SOLD">Items Sold</label>
                <input
                    type="number"
                    name="ITEMS_SOLD"
                    id="ITEMS_SOLD"
                    value={product.ITEMS_SOLD}
                    onChange={handleChange}
                    step="1"
                    // Generally, this field might be disabled or not shown on create form
                    // For edit, it might be relevant if admin needs to adjust it.
                />
                {errors.ITEMS_SOLD && <p className="error-text">{errors.ITEMS_SOLD}</p>}
            </div>

            <button type="submit" className="btn btn-primary">
                {isEditMode ? 'Update Product' : 'Add Product'}
            </button>
        </form>
    );
};

export default ProductForm;
