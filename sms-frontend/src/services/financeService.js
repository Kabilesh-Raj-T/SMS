import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'; // Backend API URL

// Fetch profit by product
export const getProfitByProduct = async () => {
    try {
        const response = await axios.get(`${API_URL}/finance/profit-by-product`);
        return response.data;
    } catch (error) {
        console.error("Error fetching profit by product:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Fetch total profit or loss
export const getTotalProfitLoss = async () => {
    try {
        const response = await axios.get(`${API_URL}/finance/total-profit-loss`);
        return response.data;
    } catch (error) {
        console.error("Error fetching total profit/loss:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

const financeService = {
    getProfitByProduct,
    getTotalProfitLoss,
};

export default financeService;
