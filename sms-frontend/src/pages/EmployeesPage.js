import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import employeeService from '../services/employeeService';
import './EmployeesPage.css'; // To be created

const EmployeesPage = () => {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchEmployees = async () => {
            try {
                setLoading(true);
                const data = await employeeService.getAllEmployees();
                setEmployees(data);
                setError(null);
            } catch (err) {
                setError(err.message || 'Failed to fetch employees');
                setEmployees([]);
            } finally {
                setLoading(false);
            }
        };

        fetchEmployees();
    }, []);

    const handleDeleteEmployee = async (employeeId) => {
        if (window.confirm('Are you sure you want to delete this employee?')) {
            try {
                await employeeService.deleteEmployee(employeeId);
                setEmployees(employees.filter(e => e.ID !== employeeId));
                alert('Employee deleted successfully!');
            } catch (err) {
                alert('Failed to delete employee: ' + (err.error || err.message));
            }
        }
    };

    if (loading) {
        return <p>Loading employees...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    return (
        <div className="employees-page">
            <h1>Employees Management</h1>
            <Link to="/employees/add" className="btn btn-primary add-employee-link">Add New Employee</Link>

            {employees.length === 0 ? (
                <p>No employees found.</p>
            ) : (
                <table className="employees-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Contact</th>
                            <th>Gender</th>
                            <th>Position</th>
                            <th>Salary</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {employees.map(employee => (
                            <tr key={employee.ID}>
                                <td>{employee.ID}</td>
                                <td>{employee.NAME}</td>
                                <td>{employee.CONTACT_NUMBER}</td>
                                <td>{employee.GENDER}</td>
                                <td>{employee.POSITION}</td>
                                <td>{employee.SALARY ? `$${Number(employee.SALARY).toFixed(2)}` : 'N/A'}</td>
                                <td className="employee-actions">
                                    <Link to={`/employees/edit/${employee.ID}`} className="btn btn-secondary btn-sm">Edit</Link>
                                    <button onClick={() => handleDeleteEmployee(employee.ID)} className="btn btn-danger btn-sm">Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default EmployeesPage;
