import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">SMS</Link>
            <ul className="navbar-nav">
                <li className="nav-item">
                    <Link to="/products" className="nav-link">Products</Link>
                </li>
                <li className="nav-item">
                    <Link to="/purchase" className="nav-link">Make Purchase</Link>
                </li>
                <li className="nav-item">
                    <Link to="/customers" className="nav-link">Customers</Link>
                </li>
                <li className="nav-item">
                    <Link to="/employees" className="nav-link">Employees</Link>
                </li>
                <li className="nav-item">
                    <Link to="/finance" className="nav-link">Finance</Link>
                </li>
                <li className="nav-item">
                    <Link to="/stats" className="nav-link">Stats</Link>
                </li>
            </ul>
        </nav>
    );
};

export default Navbar;
