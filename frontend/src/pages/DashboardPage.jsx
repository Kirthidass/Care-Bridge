import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { uploadReport, getDocuments, getExplanation, chatWithReport } from '../services/api';

function DashboardPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const fileInputRef = useRef(null);
    const chatEndRef = useRef(null);

    const [role, setRole] = useState('patient');
    const [reports, setReports] = useState([]);
    const [activeReport, setActiveReport] = useState(null);
    const [explanation, setExplanation] = useState(null);
    const [loading, setLoading] = useState(false);
    const [view, setView] = useState('list'); // 'list' or 'detail'

    // Chat state
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [chatLoading, setChatLoading] = useState(false);

    const loadReports = useCallback(async () => {
        try {
            const docs = await getDocuments();
            setReports(docs);
            
            // If active report was deleted, clear it
            if (activeReport && !docs.find(d => d.id === activeReport.id)) {
                setActiveReport(null);
                setExplanation(null);
                setChatMessages([]);
                setView('list');
            }
        } catch (err) {
            console.error('Failed to load documents:', err);
        }
    }, [activeReport]);

    useEffect(() => {
        const savedRole = localStorage.getItem('userRole') || 'patient';
        setRole(savedRole);
        loadReports();
    }, []);

    // Reload reports when navigating back to dashboard (e.g., after deleting from manage page)
    useEffect(() => {
        loadReports();
    }, [location.key]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setLoading(true);
        setChatMessages([]);

        try {
            const result = await uploadReport(file, role);
            await loadReports();

            const newReport = {
                id: result.report_id,
                filename: file.name,
                upload_date: new Date().toISOString(),
                parsed_data: result.data
            };

            setActiveReport(newReport);
            await fetchExplanation(result.report_id);
            setView('detail');
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchExplanation = async (reportId) => {
        setLoading(true);
        try {
            const result = await getExplanation(reportId, role);
            setExplanation(result);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const selectReport = (report) => {
        setActiveReport(report);
        setChatMessages([]);
        fetchExplanation(report.id);
        setView('detail');
    };

    const handleLogout = () => {
        localStorage.clear();
        navigate('/');
    };

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatInput.trim() || !activeReport) return;

        const userMessage = chatInput.trim();
        setChatInput('');
        setChatMessages(prev => [...prev, {
            role: 'user',
            text: userMessage,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
        setChatLoading(true);

        try {
            const result = await chatWithReport(activeReport.id, userMessage, role);
            setChatMessages(prev => [...prev, {
                role: 'assistant',
                text: result.answer,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);
        } catch (err) {
            setChatMessages(prev => [...prev, {
                role: 'assistant',
                text: 'Sorry, I could not process your question. Please try again.',
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);
        } finally {
            setChatLoading(false);
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
                    <button
                        className={`nav-item ${view === 'list' && !activeReport ? 'active' : ''}`}
                        onClick={() => { setView('list'); setActiveReport(null); }}
                    >
                        <span className="nav-item-icon">📁</span>
                        Documents
                    </button>

                    <button
                        className={`nav-item ${view === 'list' && reports.length > 0 ? 'active' : ''}`}
                        onClick={() => setView('list')}
                    >
                        <span className="nav-item-icon">📋</span>
                        Lab Reports
                    </button>

                    <button
                        className="nav-item"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <span className="nav-item-icon">📤</span>
                        Upload New Report
                    </button>

                    <button
                        className="nav-item"
                        onClick={() => navigate('/manage-documents')}
                    >
                        <span className="nav-item-icon">⚙️</span>
                        Manage Documents
                    </button>
                </nav>

                <div className="sidebar-footer">
                    <button className="nav-item" onClick={handleLogout}>
                        <span className="nav-item-icon">🚪</span>
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Area */}
            <div className="main-area">
                {/* Top Header */}
                <header className="top-header">
                    <div className="header-left">
                        <input
                            type="file"
                            ref={fileInputRef}
                            style={{ display: 'none' }}
                            onChange={handleFileUpload}
                            accept=".pdf,.png,.jpg,.jpeg"
                        />
                    </div>

                    <div className="header-right">
                        <div className="mode-badge">
                            {role === 'patient' ? '👤 Patient Mode' : '🩺 Clinician Mode'}
                        </div>
                        <div className="user-avatar">
                            {localStorage.getItem('userEmail')?.charAt(0).toUpperCase() || 'U'}
                        </div>
                    </div>
                </header>

                {/* Content + Chat */}
                <div className="content-wrapper">
                    <main className="content-main">
                        {loading ? (
                            <div style={{ padding: '3rem', textAlign: 'center' }}>
                                <div className="loading-spinner"></div>
                                <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Processing...</p>
                            </div>
                        ) : view === 'list' ? (
                            /* Reports List View */
                            <>
                                <div className="reports-header">
                                    <h2 className="reports-title">My Reports</h2>
                                    <button className="btn-upload" onClick={() => fileInputRef.current?.click()}>
                                        📤 Upload New Report
                                    </button>
                                </div>

                                {reports.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="empty-state-icon">📄</div>
                                        <h3>No Reports Yet</h3>
                                        <p>Upload a medical report to get started</p>
                                    </div>
                                ) : (
                                    <div className="report-list">
                                        {reports.map((report) => (
                                            <div
                                                key={report.id}
                                                className={`report-item ${activeReport?.id === report.id ? 'active' : ''}`}
                                                onClick={() => selectReport(report)}
                                            >
                                                <div className="report-icon">📋</div>
                                                <div className="report-info">
                                                    <div className="report-name">{report.filename}</div>
                                                    <div className="report-meta">
                                                        Report Date: {report.parsed_data?.report_date || formatDate(report.upload_date)}
                                                    </div>
                                                </div>
                                                <div className="report-status">
                                                    <span className="status-badge active">Active</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        ) : (
                            /* Report Detail View */
                            <div className="report-detail">
                                <button className="back-btn" onClick={() => setView('list')}>
                                    ← Back to Reports
                                </button>

                                <div className="report-detail-header">
                                    <div className="report-detail-title">
                                        {activeReport?.filename || 'Lab Report'}
                                    </div>
                                    <div className="report-detail-date">
                                        Report Date: {activeReport?.parsed_data?.report_date || formatDate(activeReport?.upload_date)} | 
                                        Uploaded: {formatDate(activeReport?.upload_date)}
                                    </div>
                                </div>

                                {/* Test Results Table */}
                                {activeReport?.parsed_data?.tests && (
                                    <div className="card">
                                        <div className="card-header">
                                            <h3 className="card-title">Test Results</h3>
                                        </div>
                                        <div className="card-content">
                                            <div className="results-table">
                                                {activeReport.parsed_data.tests.map((test, idx) => (
                                                    <div key={idx} className="result-row">
                                                        <div className="result-test">
                                                            <div className="result-name">{test.name}</div>
                                                            <div className="result-range">Range: {test.range}</div>
                                                        </div>
                                                        <div className="result-value">
                                                            <span className={`value-badge ${test.status}`}>
                                                                {test.value} {test.unit}
                                                            </span>
                                                            <span className={`status-indicator ${test.status}`}>
                                                                {test.status === 'normal' ? '✓' : '⚠'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* AI Explanation */}
                                {explanation && (
                                    <div className="card">
                                        <div className="card-header">
                                            <h3 className="card-title">
                                                {role === 'patient' ? '💡 Your Report Explained' : '🩺 Clinical Summary'}
                                            </h3>
                                            <span className="ai-badge">🤖 AI-Generated</span>
                                        </div>
                                        <div className="card-content explanation-content">
                                            <div dangerouslySetInnerHTML={{ 
                                                __html: (explanation?.explanation || 'Loading explanation...').replace(/\n/g, '<br/>') 
                                            }} />
                                        </div>
                                    </div>
                                )}

                                {/* Safety Warnings */}
                                {explanation?.safety_warnings && explanation.safety_warnings.length > 0 && (
                                    <div className="card warning-card">
                                        <div className="card-header">
                                            <h3 className="card-title">⚠️ Important Notes</h3>
                                        </div>
                                        <div className="card-content">
                                            {explanation.safety_warnings.map((warning, idx) => (
                                                <div key={idx} className="warning-item">
                                                    • {warning}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Contextual Message */}
                                {explanation?.contextual_message && (
                                    <div className="card contextual-note">
                                        <div className="card-header">
                                            <h3 className="card-title">📅 Contextual Information</h3>
                                        </div>
                                        <div className="card-content">
                                            <p>{explanation.contextual_message}</p>
                                        </div>
                                    </div>
                                )}

                                {/* Disclaimer */}
                                <div className="card disclaimer">
                                    <div className="disclaimer-content">
                                        <p>
                                            <strong>⚠️ Important Disclaimer:</strong> {explanation?.disclaimer || 
                                            'This information is for educational purposes only and is not a medical diagnosis. Please consult your healthcare provider for interpretation.'}
                                        </p>
                                        {explanation?.citations && explanation.citations.length > 0 && (
                                            <p style={{ marginTop: '0.75rem', fontSize: '0.9rem' }}>
                                                <strong>Sources:</strong> {explanation.citations.join(', ')}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </main>

                    {/* Chat Panel */}
                    <aside className="chat-panel">
                        <div className="chat-header">
                            <span className="chat-header-title">💬 Ask About This Report</span>
                            <button className="chat-close">×</button>
                        </div>

                        <div className="chat-context">
                            Using document: {activeReport?.filename || 'Select a report'}
                        </div>

                        <div className="chat-messages">
                            {chatMessages.length === 0 && (
                                <div className="empty-state" style={{ padding: '2rem 1rem' }}>
                                    <p>👋 Ask me anything about your report</p>
                                    <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                        I can explain values but cannot diagnose
                                    </p>
                                </div>
                            )}

                            {chatMessages.map((msg, idx) => (
                                <div key={idx} className={`chat-message ${msg.role}`}>
                                    <div className="chat-avatar">
                                        {msg.role === 'user' ? '👤' : '🤖'}
                                    </div>
                                    <div>
                                        <div className="chat-bubble">{msg.text}</div>
                                        <div className="chat-time">{msg.time}</div>
                                    </div>
                                </div>
                            ))}

                            {chatLoading && (
                                <div className="chat-message assistant">
                                    <div className="chat-avatar">🤖</div>
                                    <div className="chat-bubble">
                                        <div className="typing-indicator">
                                            <span></span><span></span><span></span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={chatEndRef} />
                        </div>

                        <form className="chat-input-area" onSubmit={handleChatSubmit}>
                            <input
                                type="text"
                                className="chat-input"
                                placeholder={activeReport ? "Ask a question..." : "Select a report first"}
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                disabled={!activeReport || chatLoading}
                            />
                            <button
                                type="submit"
                                className="chat-send"
                                disabled={!activeReport || chatLoading || !chatInput.trim()}
                            >
                                ➤
                            </button>
                        </form>
                    </aside>
                </div>
            </div>
        </div>
    );
}

export default DashboardPage;
