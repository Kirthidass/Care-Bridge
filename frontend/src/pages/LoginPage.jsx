import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);

    const handleLogin = (e) => {
        e.preventDefault();
        // Demo login - just navigate
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('userEmail', email || 'demo@carebridge.ai');
        navigate('/select-role');
    };

    return (
        <div className="login-page">
            <div className="login-card">
                <div className="login-logo">
                    <div className="login-logo-icon">🏥</div>
                    <span className="login-logo-text">CARE-BRIDGE AI</span>
                </div>

                <h1 className="login-title">Welcome to CARE-BRIDGE AI</h1>
                <p className="login-subtitle">Your Health Report Assistant</p>

                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <input
                            type="email"
                            className="form-input"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="form-group">
                        <input
                            type="password"
                            className="form-input"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    <label className="form-checkbox">
                        <input
                            type="checkbox"
                            checked={rememberMe}
                            onChange={(e) => setRememberMe(e.target.checked)}
                        />
                        Remember me
                    </label>

                    <button type="submit" className="btn-primary">
                        Login
                    </button>
                </form>

                <div className="login-links">
                    <a href="#">Forgot Password?</a>
                    <a href="#">Sign Up</a>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
