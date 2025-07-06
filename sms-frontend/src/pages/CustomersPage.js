import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import customerService from '../services/customerService';
import './CustomersPage.css'; // We'll create this for styling

const CustomersPage = () => {
    const [customers, setCustomers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCustomers = async () => {
            try {
                setLoading(true);
                const data = await customerService.getAllCustomers();
                setCustomers(data);
                setError(null);
            } catch (err) {
                setError(err.message || 'Failed to fetch customers');
                setCustomers([]);
            } finally {
                setLoading(false);
            }
        };

        fetchCustomers();
    }, []);

    const handleDeleteCustomer = async (customerId) => {
        if (window.confirm('Are you sure you want to delete this customer?')) {
            try {
                await customerService.deleteCustomer(customerId);
                setCustomers(customers.filter(c => c.ID !== customerId));
                alert('Customer deleted successfully!');
            } catch (err) {
                alert('Failed to delete customer: ' + (err.error || err.message));
            }
        }
    };

    if (loading) {
        return <p>Loading customers...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    return (
        <div className="customers-page">
            <h1>Customers Management</h1>
            <Link to="/customers/add" className="btn btn-primary add-customer-link">Add New Customer</Link>

            {customers.length === 0 ? (
                <p>No customers found.</p>
            ) : (
                <table className="customers-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Contact</th>
                            <th>Gender</th>
                            <th>Email</th>
                            {/* PURCHASES_LIST can be complex to display in a table row directly */}
                            {/* Consider a detail view or tooltip if needed */}
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {customers.map(customer => (
                            <tr key={customer.ID}>
                                <td>{customer.ID}</td>
                                <td>{customer.NAME}</td>
                                <td>{customer.CONTACT_NUMBER}</td>
                                <td>{customer.GENDER || 'N/A'}</td>
                                <td>{customer.EMAIL || 'N/A'}</td>
                                <td className="customer-actions">
                                    <Link to={`/customers/edit/${customer.ID}`} className="btn btn-secondary btn-sm">Edit</Link>
                                    {/* <button onClick={() => alert(`View purchases for ${customer.NAME}`)} className="btn btn-info btn-sm">View Purchases</button> */}
                                    <button onClick={() => handleDeleteCustomer(customer.ID)} className="btn btn-danger btn-sm">Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default CustomersPage;
