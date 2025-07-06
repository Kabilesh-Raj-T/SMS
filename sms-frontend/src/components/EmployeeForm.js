import React, { useState, useEffect } from 'react';
// Reusing ProductForm.css for styling consistency, can be generalized later
import './ProductForm.css';

const EmployeeForm = ({ onSubmit, initialData = null, isEditMode = false }) => {
    const [employee, setEmployee] = useState({
        ID: '',
        NAME: '',
        CONTACT_NUMBER: '',
        GENDER: '',
        POSITION: '',
        SALARY: ''
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (initialData) {
            const stringifiedData = Object.keys(initialData).reduce((acc, key) => {
                acc[key] = initialData[key] !== null && initialData[key] !== undefined ? String(initialData[key]) : '';
                return acc;
            }, {});
            setEmployee(stringifiedData);
        } else {
            setEmployee({ ID: '', NAME: '', CONTACT_NUMBER: '', GENDER: '', POSITION: '', SALARY: '' });
        }
    }, [initialData]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setEmployee(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        if (!employee.ID && !isEditMode) newErrors.ID = "Employee ID is required.";
        if (!employee.NAME) newErrors.NAME = "Employee Name is required.";
        if (!employee.CONTACT_NUMBER) {
            newErrors.CONTACT_NUMBER = "Contact Number is required.";
        } else if (!/^\d+$/.test(employee.CONTACT_NUMBER)) {
            newErrors.CONTACT_NUMBER = "Contact Number must contain only digits.";
        }
        if (!employee.GENDER) newErrors.GENDER = "Gender is required.";
        if (!employee.POSITION) newErrors.POSITION = "Position is required.";
        if (!employee.SALARY || isNaN(parseFloat(employee.SALARY)) || parseFloat(employee.SALARY) < 0) {
            newErrors.SALARY = "Valid Salary is required (must be a non-negative number).";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (validateForm()) {
            const employeeDataToSubmit = {
                ...employee,
                SALARY: parseFloat(employee.SALARY) // Convert SALARY to number
            };
            onSubmit(employeeDataToSubmit);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="product-form"> {/* Reusing .product-form class for styling */}
            <div className="form-group">
                <label htmlFor="ID">Employee ID</label>
                <input
                    type="text"
                    name="ID"
                    id="ID"
                    value={employee.ID}
                    onChange={handleChange}
                    disabled={isEditMode}
                />
                {errors.ID && <p className="error-text">{errors.ID}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="NAME">Name</label>
                <input
                    type="text"
                    name="NAME"
                    id="NAME"
                    value={employee.NAME}
                    onChange={handleChange}
                />
                {errors.NAME && <p className="error-text">{errors.NAME}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="CONTACT_NUMBER">Contact Number</label>
                <input
                    type="text"
                    name="CONTACT_NUMBER"
                    id="CONTACT_NUMBER"
                    value={employee.CONTACT_NUMBER}
                    onChange={handleChange}
                />
                {errors.CONTACT_NUMBER && <p className="error-text">{errors.CONTACT_NUMBER}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="GENDER">Gender</label>
                <input // Could be a select dropdown for better UX: <select name="GENDER" value={employee.GENDER} onChange={handleChange}> <option value="">Select Gender</option> <option value="Male">Male</option> <option value="Female">Female</option> <option value="Other">Other</option> </select>
                    type="text"
                    name="GENDER"
                    id="GENDER"
                    value={employee.GENDER}
                    onChange={handleChange}
                />
                {errors.GENDER && <p className="error-text">{errors.GENDER}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="POSITION">Position</label>
                <input
                    type="text"
                    name="POSITION"
                    id="POSITION"
                    value={employee.POSITION}
                    onChange={handleChange}
                />
                {errors.POSITION && <p className="error-text">{errors.POSITION}</p>}
            </div>

            <div className="form-group">
                <label htmlFor="SALARY">Salary</label>
                <input
                    type="number"
                    name="SALARY"
                    id="SALARY"
                    value={employee.SALARY}
                    onChange={handleChange}
                    step="0.01"
                />
                {errors.SALARY && <p className="error-text">{errors.SALARY}</p>}
            </div>

            <button type="submit" className="btn btn-primary">
                {isEditMode ? 'Update Employee' : 'Add Employee'}
            </button>
        </form>
    );
};

export default EmployeeForm;
