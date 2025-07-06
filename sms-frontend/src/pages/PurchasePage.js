import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import productService from '../services/productService';
import customerService from '../services/customerService'; // May need for customer lookup or validation
import './PurchasePage.css'; // To be created

const PurchasePage = () => {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [cart, setCart] = useState([]); // [{ product_id: '', name: '', quantity: 1, price: 0, stock: 0 }]
    const [customerContact, setCustomerContact] = useState('');
    const [customerNameIfNew, setCustomerNameIfNew] = useState('');
    const [isNewCustomer, setIsNewCustomer] = useState(false); // To conditionally show name input

    const [loadingProducts, setLoadingProducts] = useState(true);
    const [error, setError] = useState(null);
    const [submitError, setSubmitError] = useState(null);
    const [submitSuccess, setSubmitSuccess] = useState('');


    // Fetch all products for selection
    useEffect(() => {
        const fetchProducts = async () => {
            try {
                setLoadingProducts(true);
                const data = await productService.getAllProducts();
                // Filter out products with 0 quantity or map them if needed
                setProducts(data.filter(p => p.QUANTITY > 0));
                setError(null);
            } catch (err) {
                setError(err.message || 'Failed to fetch products');
                setProducts([]);
            } finally {
                setLoadingProducts(false);
            }
        };
        fetchProducts();
    }, []);

    // Function to add product to cart
    const handleAddToCart = (product) => {
        if (product.QUANTITY <= 0) {
            alert("This product is out of stock.");
            return;
        }
        setCart(prevCart => {
            const existingItem = prevCart.find(item => item.product_id === product.ID);
            if (existingItem) {
                // Increase quantity if item already in cart, up to stock limit
                const newQuantity = existingItem.quantity + 1;
                if (newQuantity > product.QUANTITY) {
                    alert(`Cannot add more than available stock: ${product.QUANTITY}`);
                    return prevCart;
                }
                return prevCart.map(item =>
                    item.product_id === product.ID ? { ...item, quantity: newQuantity } : item
                );
            } else {
                // Add new item to cart
                return [...prevCart, {
                    product_id: product.ID,
                    name: product.NAME,
                    quantity: 1,
                    price: product.SELLING_PRICE,
                    stock: product.QUANTITY // Keep track of stock for validation
                }];
            }
        });
    };

    // Function to update quantity in cart
    const handleUpdateQuantity = (productId, newQuantity) => {
        const numQuantity = parseInt(newQuantity, 10);
        setCart(prevCart =>
            prevCart.map(item => {
                if (item.product_id === productId) {
                    if (numQuantity <= 0) return null; // Will be filtered out
                    if (numQuantity > item.stock) {
                        alert(`Quantity cannot exceed available stock: ${item.stock}`);
                        return { ...item, quantity: item.stock };
                    }
                    return { ...item, quantity: numQuantity };
                }
                return item;
            }).filter(Boolean) // Remove null items (quantity <= 0)
        );
    };

    // Function to remove item from cart
    const handleRemoveFromCart = (productId) => {
        setCart(prevCart => prevCart.filter(item => item.product_id !== productId));
    };

    // Calculate total price
    const totalPrice = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

    // Handle purchase submission
    const handleSubmitPurchase = async (e) => {
        e.preventDefault();
        setSubmitError(null);
        setSubmitSuccess('');

        if (cart.length === 0) {
            setSubmitError("Your cart is empty.");
            return;
        }
        if (!customerContact.trim()) {
            setSubmitError("Customer contact number is required.");
            return;
        }
        if (isNewCustomer && !customerNameIfNew.trim()) {
            setSubmitError("Customer name is required for new customers.");
            return;
        }

        const purchaseData = {
            customer_contact: customerContact,
            items: cart.map(item => ({ product_id: item.product_id, quantity: item.quantity })),
            ...(isNewCustomer && { customer_name: customerNameIfNew }) // Conditionally add customer_name
        };

        try {
            const result = await productService.makePurchase(purchaseData);
            setSubmitSuccess(result.message || "Purchase successful!");
            setCart([]); // Clear cart
            setCustomerContact('');
            setCustomerNameIfNew('');
            setIsNewCustomer(false);
            // Optionally, redirect or update product list if stock changes are significant
            // navigate('/products');
        } catch (err) {
            console.error("Purchase failed:", err);
            setSubmitError(err.error || err.message || "Failed to complete purchase.");
        }
    };

    // Basic check if customer exists - could be more sophisticated
    // For now, just using a checkbox to toggle new customer name field
    // A real scenario might involve an API call to check customer by contact on blur/change

    if (loadingProducts) return <p>Loading products for purchase...</p>;
    if (error) return <p className="error-message">Error loading products: {error}</p>;

    return (
        <div className="purchase-page">
            <h1>Make a Purchase</h1>

            <div className="purchase-layout">
                <div className="product-selection-area">
                    <h2>Available Products</h2>
                    {products.length === 0 && <p>No products currently available for purchase.</p>}
                    <div className="product-list">
                        {products.map(product => (
                            <div key={product.ID} className="product-item-purchase">
                                <span>{product.NAME} (${product.SELLING_PRICE.toFixed(2)}) - Stock: {product.QUANTITY}</span>
                                <button onClick={() => handleAddToCart(product)} disabled={product.QUANTITY <= 0}>
                                    Add to Cart
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="cart-and-customer-area">
                    <h2>Shopping Cart</h2>
                    {cart.length === 0 ? (
                        <p>Your cart is empty.</p>
                    ) : (
                        <table className="cart-table">
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Total</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cart.map(item => (
                                    <tr key={item.product_id}>
                                        <td>{item.name}</td>
                                        <td>
                                            <input
                                                type="number"
                                                value={item.quantity}
                                                onChange={(e) => handleUpdateQuantity(item.product_id, e.target.value)}
                                                min="1"
                                                max={item.stock}
                                            />
                                        </td>
                                        <td>${item.price.toFixed(2)}</td>
                                        <td>${(item.price * item.quantity).toFixed(2)}</td>
                                        <td>
                                            <button onClick={() => handleRemoveFromCart(item.product_id)} className="btn-remove">
                                                Remove
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                    {cart.length > 0 && <h3 className="cart-total">Total: ${totalPrice.toFixed(2)}</h3>}

                    <h2>Customer Information</h2>
                    <form onSubmit={handleSubmitPurchase} className="customer-purchase-form">
                        <div className="form-group">
                            <label htmlFor="customerContact">Customer Contact Number:</label>
                            <input
                                type="text"
                                id="customerContact"
                                value={customerContact}
                                onChange={(e) => setCustomerContact(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={isNewCustomer}
                                    onChange={(e) => setIsNewCustomer(e.target.checked)}
                                />
                                New Customer?
                            </label>
                        </div>
                        {isNewCustomer && (
                            <div className="form-group">
                                <label htmlFor="customerNameIfNew">Customer Name:</label>
                                <input
                                    type="text"
                                    id="customerNameIfNew"
                                    value={customerNameIfNew}
                                    onChange={(e) => setCustomerNameIfNew(e.target.value)}
                                    required={isNewCustomer}
                                />
                            </div>
                        )}
                        <button type="submit" className="btn btn-primary" disabled={cart.length === 0}>
                            Complete Purchase
                        </button>
                        {submitError && <p className="error-message submit-error">{submitError}</p>}
                        {submitSuccess && <p className="success-message submit-success">{submitSuccess}</p>}
                    </form>
                </div>
            </div>
        </div>
    );
};

export default PurchasePage;
