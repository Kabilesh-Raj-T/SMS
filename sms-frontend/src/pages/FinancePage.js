import React, { useState, useEffect } from 'react';
import financeService from '../services/financeService';
import './FinancePage.css'; // To be created

const FinancePage = () => {
    const [profitByProduct, setProfitByProduct] = useState([]);
    const [totalProfitLoss, setTotalProfitLoss] = useState(null);
    const [loadingPBP, setLoadingPBP] = useState(true);
    const [loadingTPL, setLoadingTPL] = useState(true);
    const [errorPBP, setErrorPBP] = useState(null);
    const [errorTPL, setErrorTPL] = useState(null);

    useEffect(() => {
        const fetchProfitByProduct = async () => {
            try {
                setLoadingPBP(true);
                const data = await financeService.getProfitByProduct();
                setProfitByProduct(data);
                setErrorPBP(null);
            } catch (err) {
                setErrorPBP(err.message || 'Failed to fetch profit by product');
                setProfitByProduct([]);
            } finally {
                setLoadingPBP(false);
            }
        };

        const fetchTotalProfitLoss = async () => {
            try {
                setLoadingTPL(true);
                const data = await financeService.getTotalProfitLoss();
                setTotalProfitLoss(data);
                setErrorTPL(null);
            } catch (err) {
                setErrorTPL(err.message || 'Failed to fetch total profit/loss');
                setTotalProfitLoss(null);
            } finally {
                setLoadingTPL(false);
            }
        };

        fetchProfitByProduct();
        fetchTotalProfitLoss();
    }, []);

    return (
        <div className="finance-page">
            <h1>Finance Reports</h1>

            <section className="finance-section">
                <h2>Total Profit/Loss</h2>
                {loadingTPL && <p>Loading total profit/loss...</p>}
                {errorTPL && <p className="error-message">Error: {errorTPL}</p>}
                {totalProfitLoss && !loadingTPL && !errorTPL && (
                    <div className={`total-profit-loss-display ${totalProfitLoss.status}`}>
                        Overall Status: <span className="status-value">{totalProfitLoss.status}</span>
                        <br />
                        Amount: <span className="amount-value">${Math.abs(totalProfitLoss.total_profit_loss).toFixed(2)}</span>
                    </div>
                )}
            </section>

            <section className="finance-section">
                <h2>Profitability by Product</h2>
                {loadingPBP && <p>Loading profit by product data...</p>}
                {errorPBP && <p className="error-message">Error: {errorPBP}</p>}
                {!loadingPBP && !errorPBP && profitByProduct.length === 0 && <p>No product profitability data available.</p>}
                {!loadingPBP && !errorPBP && profitByProduct.length > 0 && (
                    <table className="finance-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Selling Price</th>
                                <th>Cost Price</th>
                                <th>Items Sold</th>
                                <th>Revenue</th>
                                <th>COGS</th>
                                <th>Profit/Loss</th>
                            </tr>
                        </thead>
                        <tbody>
                            {profitByProduct.map(p => (
                                <tr key={p.ID} className={p.PROFIT_LOSS >= 0 ? 'profit' : 'loss'}>
                                    <td>{p.ID}</td>
                                    <td>{p.NAME}</td>
                                    <td>${p.SELLING_PRICE ? p.SELLING_PRICE.toFixed(2) : 'N/A'}</td>
                                    <td>${p.COST_PRICE ? p.COST_PRICE.toFixed(2) : 'N/A'}</td>
                                    <td>{p.ITEMS_SOLD}</td>
                                    <td>${p.REVENUE ? p.REVENUE.toFixed(2) : 'N/A'}</td>
                                    <td>${p.COGS ? p.COGS.toFixed(2) : 'N/A'}</td>
                                    <td>${p.PROFIT_LOSS ? p.PROFIT_LOSS.toFixed(2) : 'N/A'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </section>
        </div>
    );
};

export default FinancePage;
