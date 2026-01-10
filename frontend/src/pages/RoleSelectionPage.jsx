import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function RoleSelectionPage() {
    const navigate = useNavigate();
    const [selectedRole, setSelectedRole] = useState(null);

    const handleContinue = () => {
        if (selectedRole) {
            localStorage.setItem('userRole', selectedRole);
            navigate('/dashboard');
        }
    };

    return (
        <div className="role-page">
            <div className="role-header">
                <div className="login-logo-icon">🏥</div>
                <span className="login-logo-text">CARE-BRIDGE AI</span>
            </div>

            <h1 className="role-title">Select Your Role</h1>
            <p className="role-subtitle">How would you like to view your reports?</p>

            <div className="role-cards">
                <div
                    className={`role-card ${selectedRole === 'patient' ? 'selected' : ''}`}
                    onClick={() => setSelectedRole('patient')}
                >
                    <div className="role-card-icon">👤</div>
                    <div className="role-card-content">
                        <h3>Patient</h3>
                        <p>Understand My Results</p>
                    </div>
                </div>

                <div
                    className={`role-card ${selectedRole === 'clinician' ? 'selected' : ''}`}
                    onClick={() => setSelectedRole('clinician')}
                >
                    <div className="role-card-icon">🩺</div>
                    <div className="role-card-content">
                        <h3>Clinician</h3>
                        <p>Summarize Key Findings</p>
                    </div>
                </div>
            </div>

            <button
                className="btn-primary btn-continue"
                onClick={handleContinue}
                disabled={!selectedRole}
                style={{ opacity: selectedRole ? 1 : 0.5 }}
            >
                Continue
            </button>
        </div>
    );
}

export default RoleSelectionPage;
