import React, { useState, useEffect } from 'react';
import statsService from '../services/statsService';
import './StatsPage.css'; // To be created

const StatsPage = () => {
    const [bestSelling, setBestSelling] = useState(null);
    const [mostProfitable, setMostProfitable] = useState(null);
    const [leastSelling, setLeastSelling] = useState(null);

    const [loadingBS, setLoadingBS] = useState(true);
    const [loadingMP, setLoadingMP] = useState(true);
    const [loadingLS, setLoadingLS] = useState(true);

    const [errorBS, setErrorBS] = useState(null);
    const [errorMP, setErrorMP] = useState(null);
    const [errorLS, setErrorLS] = useState(null);

    useEffect(() => {
        const fetchBestSelling = async () => {
            try {
                setLoadingBS(true);
                const data = await statsService.getBestSellingProduct();
                setBestSelling(data);
                setErrorBS(null);
            } catch (err) {
                setErrorBS(err.message || 'Failed to fetch best selling product');
                setBestSelling(null);
            } finally {
                setLoadingBS(false);
            }
        };

        const fetchMostProfitable = async () => {
            try {
                setLoadingMP(true);
                const data = await statsService.getMostProfitableProduct();
                setMostProfitable(data);
                setErrorMP(null);
            } catch (err) {
                setErrorMP(err.message || 'Failed to fetch most profitable product');
                setMostProfitable(null);
            } finally {
                setLoadingMP(false);
            }
        };

        const fetchLeastSelling = async () => {
            try {
                setLoadingLS(true);
                const data = await statsService.getLeastSellingProduct();
                setLeastSelling(data);
                setErrorLS(null);
            } catch (err) {
                setErrorLS(err.message || 'Failed to fetch least selling product');
                setLeastSelling(null);
            } finally {
                setLoadingLS(false);
            }
        };

        fetchBestSelling();
        fetchMostProfitable();
        fetchLeastSelling();
    }, []);

    const renderStatCard = (title, data, loading, error) => {
        if (loading) return <p>Loading {title.toLowerCase()}...</p>;
        if (error) return <p className="error-message">Error fetching {title.toLowerCase()}: {error}</p>;
        if (!data || (data && data.message)) { // API might return a message for "not found"
            return <p>{data && data.message ? data.message : `${title} data not available.`}</p>;
        }

        return (
            <div className="stat-card-content">
                {data.name && <p><strong>Name:</strong> {data.name}</p>}
                {data.id && <p><strong>ID:</strong> {data.id}</p>}
                {data.items_sold !== undefined && <p><strong>Items Sold:</strong> {data.items_sold}</p>}
                {data.profit !== undefined && <p><strong>Profit:</strong> ${data.profit.toFixed(2)}</p>}
                {/* Add more fields if the API returns them, e.g., revenue, cogs for most profitable */}
            </div>
        );
    };


    return (
        <div className="stats-page">
            <h1>Store Statistics</h1>
            <div className="stats-container">
                <div className="stat-card">
                    <h2>📈 Best Selling Product</h2>
                    {renderStatCard("Best Selling Product", bestSelling, loadingBS, errorBS)}
                </div>

                <div className="stat-card">
                    <h2>💰 Most Profitable Product</h2>
                    {renderStatCard("Most Profitable Product", mostProfitable, loadingMP, errorMP)}
                </div>

                <div className="stat-card">
                    <h2>📉 Least Selling Product</h2>
                    {renderStatCard("Least Selling Product", leastSelling, loadingLS, errorLS)}
                </div>
            </div>
        </div>
    );
};

export default StatsPage;
