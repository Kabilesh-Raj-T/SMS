import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'; // Backend API URL

// Fetch best selling product
export const getBestSellingProduct = async () => {
    try {
        const response = await axios.get(`${API_URL}/stats/best-selling-product`);
        return response.data;
    } catch (error) {
        console.error("Error fetching best selling product:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Fetch most profitable product
export const getMostProfitableProduct = async () => {
    try {
        const response = await axios.get(`${API_URL}/stats/most-profitable-product`);
        return response.data;
    } catch (error) {
        console.error("Error fetching most profitable product:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Fetch least selling product
export const getLeastSellingProduct = async () => {
    try {
        const response = await axios.get(`${API_URL}/stats/least-selling-product`);
        return response.data;
    } catch (error) {
        console.error("Error fetching least selling product:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

const statsService = {
    getBestSellingProduct,
    getMostProfitableProduct,
    getLeastSellingProduct,
};

export default statsService;
