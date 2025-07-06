import React, { useState, useEffect } from 'react';
// Using ProductForm.css as the structure is very similar, can be renamed to Form.css later if generalized
import './ProductForm.css';

const CustomerForm = ({ onSubmit, initialData = null, isEditMode = false }) => {
    const [customer, setCustomer] = useState({
        ID: '',
        NAME: '',
        CONTACT_NUMBER: '',
        GENDER: '',
        EMAIL: ''
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (initialData) {
            const stringifiedData = Object.keys(initialData).reduce((acc, key) => {
                acc[key] = initialData[key] !== null && initialData[key] !== undefined ? String(initialData[key]) : '';
                return acc;
            }, {});
            setCustomer(stringifiedData);
        } else {
            setCustomer({ ID: '', NAME: '', CONTACT_NUMBER: '', GENDER: '', EMAIL: '' });
        }
    }, [initialData]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setCustomer(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        if (!customer.ID && !isEditMode) newErrors.ID = "Customer ID is required.";
        if (!customer.NAME) newErrors.NAME = "Customer Name is required.";
        if (!customer.CONTACT_NUMBER) {
            newErrors.CONTACT_NUMBER = "Contact Number is required.";
        } else if (!/^\d+$/.test(customer.CONTACT_NUMBER)) {
            newErrors.CONTACT_NUMBER = "Contact Number must contain only digits.";
        }
        // Email validation (basic)
        if (customer.EMAIL && !/\S+@\S+\.\S+/.test(customer.EMAIL)) {
            newErrors.EMAIL = "Email address is invalid.";
        }
        // Gender and Email are optional based on backend from what I recall, but name and contact are usually key.
        // The backend model seems to require ID, NAME, CONTACT_NUMBER. GENDER, EMAIL are optional.
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (validateForm()) {
            // No numeric fields to convert here, all are strings or handled as strings by backend
            onSubmit(customer);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="product-form"> {/* Reusing .product-form class for styling */}
            <div className="form-group">
                <label htmlFor="ID">Customer ID</label>
                <input
                    type="text"
                    name="ID"
                    id="ID"
                    value={customer.ID}
                    onChange={handleChange}
                    disabled={isEditMode}
                />
                {errors.ID && <p className="error-text">{errors.ID}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="NAME">Name</label>
                <input
                    type="text"
                    name="NAME"
                    id="NAME"
                    value={customer.NAME}
                    onChange={handleChange}
                />
                {errors.NAME && <p className="error-text">{errors.NAME}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="CONTACT_NUMBER">Contact Number</label>
                <input
                    type="text" // Using text for potential leading zeros or country codes, validation ensures digits
                    name="CONTACT_NUMBER"
                    id="CONTACT_NUMBER"
                    value={customer.CONTACT_NUMBER}
                    onChange={handleChange}
                />
                {errors.CONTACT_NUMBER && <p className="error-text">{errors.CONTACT_NUMBER}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="GENDER">Gender (Optional)</label>
                <input
                    type="text"
                    name="GENDER"
                    id="GENDER"
                    value={customer.GENDER}
                    onChange={handleChange}
                />
                {/* No specific error for GENDER unless made mandatory */}
            </div>

            <div className="form-group">
                <label htmlFor="EMAIL">Email (Optional)</label>
                <input
                    type="email"
                    name="EMAIL"
                    id="EMAIL"
                    value={customer.EMAIL}
                    onChange={handleChange}
                />
                {errors.EMAIL && <p className="error-text">{errors.EMAIL}</p>}
            </div>

            <button type="submit" className="btn btn-primary">
                {isEditMode ? 'Update Customer' : 'Add Customer'}
            </button>
        </form>
    );
};

export default CustomerForm;
