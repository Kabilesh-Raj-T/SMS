import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import EmployeeForm from '../components/EmployeeForm';
import employeeService from '../services/employeeService';

const EditEmployeePage = () => {
    const { employeeId } = useParams();
    const navigate = useNavigate();
    const [employee, setEmployee] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchEmployeeDetails = async () => {
            try {
                setLoading(true);
                const data = await employeeService.getEmployeeById(employeeId);
                setEmployee(data);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch employee details:", err);
                setError(err.message || `Failed to fetch employee details for ID ${employeeId}`);
                setEmployee(null);
            } finally {
                setLoading(false);
            }
        };

        if (employeeId) {
            fetchEmployeeDetails();
        }
    }, [employeeId]);

    const handleEditEmployee = async (employeeData) => {
        try {
            // EmployeeForm handles SALARY conversion
            await employeeService.updateEmployee(employeeId, employeeData);
            alert('Employee updated successfully!');
            navigate('/employees');
        } catch (error) {
            console.error("Failed to update employee:", error);
            alert('Failed to update employee: ' + (error.error || error.message || 'Unknown error'));
        }
    };

    if (loading) {
        return <p>Loading employee details...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    if (!employee) {
        return <p>Employee not found.</p>;
    }

    return (
        <div className="edit-employee-page">
            <h2>Edit Employee (ID: {employee.ID})</h2>
            <EmployeeForm onSubmit={handleEditEmployee} initialData={employee} isEditMode={true} />
        </div>
    );
};

export default EditEmployeePage;
