import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'; // Backend API URL

// Fetch all customers
export const getAllCustomers = async () => {
    try {
        const response = await axios.get(`${API_URL}/customers`);
        return response.data;
    } catch (error) {
        console.error("Error fetching all customers:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Fetch a single customer by ID
export const getCustomerById = async (customerId) => {
    try {
        const response = await axios.get(`${API_URL}/customers/${customerId}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching customer with ID ${customerId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Create a new customer
export const createCustomer = async (customerData) => {
    try {
        const response = await axios.post(`${API_URL}/customers`, customerData);
        return response.data;
    } catch (error) {
        console.error("Error creating customer:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Update an existing customer
export const updateCustomer = async (customerId, customerData) => {
    try {
        const response = await axios.put(`${API_URL}/customers/${customerId}`, customerData);
        return response.data;
    } catch (error) {
        console.error(`Error updating customer with ID ${customerId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Delete a customer by ID
export const deleteCustomer = async (customerId) => {
    try {
        const response = await axios.delete(`${API_URL}/customers/${customerId}`);
        return response.data;
    } catch (error) {
        console.error(`Error deleting customer with ID ${customerId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

const customerService = {
    getAllCustomers,
    getCustomerById,
    createCustomer,
    updateCustomer,
    deleteCustomer,
};

export default customerService;
