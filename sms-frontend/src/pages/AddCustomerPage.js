import React from 'react';
import { useNavigate } from 'react-router-dom';
import CustomerForm from '../components/CustomerForm';
import customerService from '../services/customerService';

const AddCustomerPage = () => {
    const navigate = useNavigate();

    const handleAddCustomer = async (customerData) => {
        try {
            // Ensure optional fields that are empty are sent as null or undefined if backend prefers,
            // or just let backend handle empty strings if that's acceptable.
            // For now, sending them as they are from the form.
            const dataToSubmit = {
                ...customerData,
                GENDER: customerData.GENDER || null, // Example: send null if empty
                EMAIL: customerData.EMAIL || null,   // Example: send null if empty
            };
            await customerService.createCustomer(dataToSubmit);
            alert('Customer added successfully!');
            navigate('/customers');
        } catch (error) {
            console.error("Failed to add customer:", error);
            alert('Failed to add customer: ' + (error.error || error.message || 'Unknown error'));
        }
    };

    return (
        <div className="add-customer-page">
            <h2>Add New Customer</h2>
            {/* Reusing product-form CSS class name for consistent styling until specific one is made */}
            <CustomerForm onSubmit={handleAddCustomer} isEditMode={false} />
        </div>
    );
};

export default AddCustomerPage;
