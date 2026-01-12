import React, { useState, useEffect, useCallback } from 'react';
import api from '../../api';
import './DuplicatesPage.css';

const DuplicatesPage = () => {
    const [activeTab, setActiveTab] = useState('clients');
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const loadDuplicates = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            // Using singular 'client' as per 404 fix
            const endpoint = activeTab === 'clients' 
                ? '/client/duplicates/' 
                : '/nomenklatura/duplicates/';
                
            const response = await api.get(endpoint);
            setItems(response.data.results || response.data);
        } catch (err) {
            console.error("Error loading duplicates:", err);
            setError("Ma'lumotlarni yuklashda xatolik yuz berdi");
        } finally {
            setLoading(false);
        }
    }, [activeTab]);

    useEffect(() => {
        loadDuplicates();
    }, [loadDuplicates]);

    return (
        <div className="duplicates-page">
            <div className="page-header">
                <h1>Dublikatlar</h1>
                <p>Turli loyihalarda takrorlangan ma'lumotlar (bir xil code_1c)</p>
            </div>

            <div className="tabs">
                <button 
                    className={`tab-btn ${activeTab === 'clients' ? 'active' : ''}`}
                    onClick={() => setActiveTab('clients')}
                >
                    Clients
                </button>
                <button 
                    className={`tab-btn ${activeTab === 'nomenklatura' ? 'active' : ''}`}
                    onClick={() => setActiveTab('nomenklatura')}
                >
                    Nomenklatura
                </button>
            </div>

            {loading && <div className="loading">Yuklanmoqda...</div>}
            {error && <div className="error">{error}</div>}

            {!loading && !error && (
                <div className="duplicates-list">
                    {items.length === 0 ? (
                        <div className="no-data">Dublikatlar topilmadi ✅</div>
                    ) : (
                        <table className="duplicates-table">
                            <thead>
                                <tr>
                                    <th>Code 1C</th>
                                    <th>Nomi</th>
                                    <th>Loyihalar soni</th>
                                    <th>Harakat</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map(item => (
                                    <tr key={item.id}>
                                        <td>{item.client_code_1c || item.code_1c}</td>
                                        <td>{item.name}</td>
                                        <td>
                                            {/* Logic to show project count if available, or just a marker */}
                                            ⚠️ Dublikat
                                        </td>
                                        <td>
                                            <button className="btn-view">Ko'rish</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
};

export default DuplicatesPage;
