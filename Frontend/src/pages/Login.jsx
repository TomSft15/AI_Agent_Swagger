/**
 * Login Page
 *
 * User authentication page with login and register forms
 */
import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const { login, register, error } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);

  // Password visibility state
  const [showPassword, setShowPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Login form state
  const [loginData, setLoginData] = useState({
    emailOrUsername: '',
    password: '',
  });

  // Register form state
  const [registerData, setRegisterData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });

  const [localError, setLocalError] = useState('');

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    setLoading(true);

    try {
      // Use emailOrUsername field for login (backend accepts both)
      const result = await login(loginData.emailOrUsername, loginData.password);

      if (!result.success) {
        setLocalError(result.error || 'Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');

    // Validation
    if (registerData.password !== registerData.confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    if (registerData.password.length < 8) {
      setLocalError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const result = await register({
        email: registerData.email,
        username: registerData.username,
        password: registerData.password,
        full_name: registerData.full_name || undefined,
      });

      if (!result.success) {
        setLocalError(result.error || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoginChange = (e) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value,
    });
    setLocalError('');
  };

  const handleRegisterChange = (e) => {
    setRegisterData({
      ...registerData,
      [e.target.name]: e.target.value,
    });
    setLocalError('');
  };

  const toggleForm = () => {
    setIsLogin(!isLogin);
    setLocalError('');
  };

  const displayError = localError || error;

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>AI Agent Platform</h1>
          <p>Manage your AI agents powered by Swagger APIs</p>
        </div>

        <div className="login-tabs">
          <button
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {displayError && (
          <div className="error-message">
            {displayError}
          </div>
        )}

        {isLogin ? (
          <form onSubmit={handleLoginSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="emailOrUsername">Email or Username</label>
              <input
                type="text"
                id="emailOrUsername"
                name="emailOrUsername"
                value={loginData.emailOrUsername}
                onChange={handleLoginChange}
                required
                placeholder="your.email@example.com or username"
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={loginData.password}
                  onChange={handleLoginChange}
                  required
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegisterSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="register-email">Email *</label>
              <input
                type="email"
                id="register-email"
                name="email"
                value={registerData.email}
                onChange={handleRegisterChange}
                required
                placeholder="your.email@example.com"
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="username">Username *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={registerData.username}
                onChange={handleRegisterChange}
                required
                placeholder="Choose a username"
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="full_name">Full Name (optional)</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={registerData.full_name}
                onChange={handleRegisterChange}
                placeholder="John Doe"
                autoComplete="name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-password">Password *</label>
              <div className="password-input-wrapper">
                <input
                  type={showRegisterPassword ? "text" : "password"}
                  id="register-password"
                  name="password"
                  value={registerData.password}
                  onChange={handleRegisterChange}
                  required
                  placeholder="At least 8 characters"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowRegisterPassword(!showRegisterPassword)}
                  aria-label={showRegisterPassword ? "Hide password" : "Show password"}
                >
                  {showRegisterPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <div className="password-input-wrapper">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={registerData.confirmPassword}
                  onChange={handleRegisterChange}
                  required
                  placeholder="Re-enter your password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Register'}
            </button>
          </form>
        )}

        <div className="login-footer">
          <p>
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button className="link-button" onClick={toggleForm}>
              {isLogin ? 'Register here' : 'Login here'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
