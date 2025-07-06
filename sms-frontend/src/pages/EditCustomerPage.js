import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CustomerForm from '../components/CustomerForm';
import customerService from '../services/customerService';

const EditCustomerPage = () => {
    const { customerId } = useParams();
    const navigate = useNavigate();
    const [customer, setCustomer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCustomerDetails = async () => {
            try {
                setLoading(true);
                const data = await customerService.getCustomerById(customerId);
                setCustomer(data);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch customer details:", err);
                setError(err.message || `Failed to fetch customer details for ID ${customerId}`);
                setCustomer(null);
            } finally {
                setLoading(false);
            }
        };

        if (customerId) {
            fetchCustomerDetails();
        }
    }, [customerId]);

    const handleEditCustomer = async (customerData) => {
        try {
            // Similar to AddCustomerPage, ensure optional fields are handled if needed
            const dataToSubmit = {
                ...customerData,
                GENDER: customerData.GENDER || null,
                EMAIL: customerData.EMAIL || null,
            };
            await customerService.updateCustomer(customerId, dataToSubmit);
            alert('Customer updated successfully!');
            navigate('/customers');
        } catch (error) {
            console.error("Failed to update customer:", error);
            alert('Failed to update customer: ' + (error.error || error.message || 'Unknown error'));
        }
    };

    if (loading) {
        return <p>Loading customer details...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    if (!customer) {
        return <p>Customer not found.</p>;
    }

    return (
        <div className="edit-customer-page">
            <h2>Edit Customer (ID: {customer.ID})</h2>
            <CustomerForm onSubmit={handleEditCustomer} initialData={customer} isEditMode={true} />
        </div>
    );
};

export default EditCustomerPage;
