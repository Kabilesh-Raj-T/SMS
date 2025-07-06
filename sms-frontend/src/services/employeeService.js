import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'; // Backend API URL

// Fetch all employees
export const getAllEmployees = async () => {
    try {
        const response = await axios.get(`${API_URL}/employees`);
        return response.data;
    } catch (error) {
        console.error("Error fetching all employees:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Fetch a single employee by ID
export const getEmployeeById = async (employeeId) => {
    try {
        const response = await axios.get(`${API_URL}/employees/${employeeId}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching employee with ID ${employeeId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Create a new employee
export const createEmployee = async (employeeData) => {
    try {
        const response = await axios.post(`${API_URL}/employees`, employeeData);
        return response.data;
    } catch (error) {
        console.error("Error creating employee:", error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Update an existing employee
export const updateEmployee = async (employeeId, employeeData) => {
    try {
        const response = await axios.put(`${API_URL}/employees/${employeeId}`, employeeData);
        return response.data;
    } catch (error) {
        console.error(`Error updating employee with ID ${employeeId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

// Delete an employee by ID
export const deleteEmployee = async (employeeId) => {
    try {
        const response = await axios.delete(`${API_URL}/employees/${employeeId}`);
        return response.data;
    } catch (error) {
        console.error(`Error deleting employee with ID ${employeeId}:`, error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Network error or server is unreachable');
    }
};

const employeeService = {
    getAllEmployees,
    getEmployeeById,
    createEmployee,
    updateEmployee,
    deleteEmployee,
};

export default employeeService;
