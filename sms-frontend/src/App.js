import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
// Product Pages
import ProductsPage from './pages/ProductsPage';
import AddProductPage from './pages/AddProductPage';
import EditProductPage from './pages/EditProductPage';
import PurchasePage from './pages/PurchasePage';
// Customer Pages
import CustomersPage from './pages/CustomersPage';
import AddCustomerPage from './pages/AddCustomerPage';
import EditCustomerPage from './pages/EditCustomerPage';
// Employee Pages
import EmployeesPage from './pages/EmployeesPage';
import AddEmployeePage from './pages/AddEmployeePage';
import EditEmployeePage from './pages/EditEmployeePage';
// Other Pages
import FinancePage from './pages/FinancePage';
import StatsPage from './pages/StatsPage';
import './App.css';

function App() {
  return (
    <>
      <Navbar />
      <div className="container">
        <Routes>
          {/* General Routes */}
          <Route path="/" element={<HomePage />} />

          {/* Product Routes */}
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/add" element={<AddProductPage />} />
          <Route path="/products/edit/:productId" element={<EditProductPage />} />
          {/* <Route path="/products/:productId" element={<ProductDetailPage />} /> */}

          {/* Purchase Route */}
          <Route path="/purchase" element={<PurchasePage />} />

          {/* Customer Routes */}
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/customers/add" element={<AddCustomerPage />} />
          <Route path="/customers/edit/:customerId" element={<EditCustomerPage />} />

          {/* Employee Routes */}
          <Route path="/employees" element={<EmployeesPage />} />
          <Route path="/employees/add" element={<AddEmployeePage />} />
          <Route path="/employees/edit/:employeeId" element={<EditEmployeePage />} />

          {/* Finance & Stats Routes */}
          <Route path="/finance" element={<FinancePage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
