import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDocuments, deleteDocument } from '../services/api';

function ManageDocumentsPage() {
    const navigate = useNavigate();
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [deleting, setDeleting] = useState(null);
    const role = localStorage.getItem('userRole') || 'patient';

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        setLoading(true);
        try {
            const docs = await getDocuments();
            setDocuments(docs);
        } catch (err) {
            console.error('Failed to load documents:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (docId) => {
        if (!window.confirm('Are you sure you want to delete this document?')) {
            return;
        }
        
        setDeleting(docId);
        try {
            await deleteDocument(docId);
            // Remove from local state after successful API call
            setDocuments(documents.filter(doc => doc.id !== docId));
        } catch (err) {
            console.error('Failed to delete document:', err);
            alert('Failed to delete document. Please try again.');
        } finally {
            setDeleting(null);
        }
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    return (
        <div className="dashboard">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-logo">
                    <div className="sidebar-logo-icon">🏥</div>
                    <span className="sidebar-logo-text">CARE-BRIDGE AI</span>
                </div>

                <nav className="sidebar-nav">
                    <button className="nav-item" onClick={() => navigate('/dashboard')}>
                        <span className="nav-item-icon">←</span>
                        Back to Dashboard
                    </button>
                </nav>
            </aside>

            {/* Main Area */}
            <div className="main-area">
                <header className="top-header">
                    <div className="header-left">
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Manage Documents</h2>
                    </div>
                    <div className="header-right">
                        <div className="mode-badge">
                            {role === 'patient' ? '👤 Patient Mode' : '🩺 Clinician Mode'}
                        </div>
                    </div>
                </header>

                <div className="content-wrapper">
                    <main className="content-main">
                        {loading ? (
                            <div className="empty-state">
                                <div className="empty-state-icon">⏳</div>
                                <h3>Loading...</h3>
                            </div>
                        ) : documents.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-state-icon">📂</div>
                                <h3>No Documents</h3>
                                <p>You haven't uploaded any reports yet</p>
                            </div>
                        ) : (
                            <div className="card">
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                                            <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600, color: 'var(--text-muted)', fontSize: '0.85rem' }}>Report Name</th>
                                            <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600, color: 'var(--text-muted)', fontSize: '0.85rem' }}>Upload Date</th>
                                            <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600, color: 'var(--text-muted)', fontSize: '0.85rem' }}>Type</th>
                                            <th style={{ padding: '1rem', textAlign: 'right', fontWeight: 600, color: 'var(--text-muted)', fontSize: '0.85rem' }}>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {documents.map((doc) => (
                                            <tr key={doc.id} style={{ borderBottom: '1px solid var(--border)' }}>
                                                <td style={{ padding: '1rem' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                        <span style={{ fontSize: '1.25rem' }}>📋</span>
                                                        {doc.filename}
                                                    </div>
                                                </td>
                                                <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                                                    {formatDate(doc.upload_date)}
                                                </td>
                                                <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                                                    {doc.type || 'Lab Report'}
                                                </td>
                                                <td style={{ padding: '1rem', textAlign: 'right' }}>
                                                    <button
                                                        onClick={() => handleDelete(doc.id)}
                                                        disabled={deleting === doc.id}
                                                        style={{
                                                            padding: '0.5rem 1rem',
                                                            background: deleting === doc.id ? '#e5e7eb' : '#fee2e2',
                                                            color: deleting === doc.id ? '#9ca3af' : '#dc2626',
                                                            border: 'none',
                                                            borderRadius: '6px',
                                                            cursor: deleting === doc.id ? 'not-allowed' : 'pointer',
                                                            fontSize: '0.85rem',
                                                            fontWeight: 500
                                                        }}
                                                    >
                                                        {deleting === doc.id ? '⏳ Deleting...' : '🗑️ Delete'}
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </main>
                </div>
            </div>
        </div>
    );
}

export default ManageDocumentsPage;
