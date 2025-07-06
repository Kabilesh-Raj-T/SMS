import React from 'react';
import { useNavigate } from 'react-router-dom';
import EmployeeForm from '../components/EmployeeForm';
import employeeService from '../services/employeeService';

const AddEmployeePage = () => {
    const navigate = useNavigate();

    const handleAddEmployee = async (employeeData) => {
        try {
            // EmployeeForm handles SALARY conversion to float
            await employeeService.createEmployee(employeeData);
            alert('Employee added successfully!');
            navigate('/employees');
        } catch (error) {
            console.error("Failed to add employee:", error);
            alert('Failed to add employee: ' + (error.error || error.message || 'Unknown error'));
        }
    };

    return (
        <div className="add-employee-page">
            <h2>Add New Employee</h2>
            <EmployeeForm onSubmit={handleAddEmployee} isEditMode={false} />
        </div>
    );
};

export default AddEmployeePage;
