import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'; // Backend API URL

// Fetch all products
export const getAllProducts = async () => {
    try {
        const response = await axios.get(`${API_URL}/products`);
        return response.data;
    } catch (error) {
        console.error("Error fetching all products:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Fetch a single product by ID
export const getProductById = async (productId) => {
    try {
        const response = await axios.get(`${API_URL}/products/${productId}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching product with ID ${productId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Create a new product
export const createProduct = async (productData) => {
    try {
        const response = await axios.post(`${API_URL}/products`, productData);
        return response.data;
    } catch (error) {
        console.error("Error creating product:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Update an existing product
export const updateProduct = async (productId, productData) => {
    try {
        const response = await axios.put(`${API_URL}/products/${productId}`, productData);
        return response.data;
    } catch (error) {
        console.error(`Error updating product with ID ${productId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Delete a product by ID
export const deleteProduct = async (productId) => {
    try {
        const response = await axios.delete(`${API_URL}/products/${productId}`);
        return response.data;
    } catch (error) {
        console.error(`Error deleting product with ID ${productId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Make a purchase
export const makePurchase = async (purchaseData) => {
    // purchaseData expected to be: { customer_contact: "...", items: [{ product_id: "...", quantity: ... }], customer_name_if_new: "..." (optional) }
    try {
        const response = await axios.post(`${API_URL}/purchases`, purchaseData);
        return response.data;
    } catch (error) {
        console.error("Error making purchase:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

const productService = {
    getAllProducts,
    getProductById,
    createProduct,
    updateProduct,
    deleteProduct,
    makePurchase,
};

export default productService;
