/**
 * Main App Component
 *
 * Sets up authentication and routing for the application
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import SwaggerView from './pages/SwaggerView';
import AgentManager from './pages/AgentManager';
import AgentCreate from './pages/AgentCreate';
import AgentEdit from './pages/AgentEdit';
import ManageKeys from './pages/ManageKeys';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Main App Content with Routes
const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/swagger/view/:swaggerId"
        element={
          <ProtectedRoute>
            <SwaggerView />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agent-manager"
        element={
          <ProtectedRoute>
            <AgentManager />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agent/create"
        element={
          <ProtectedRoute>
            <AgentCreate />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agent/edit/:agentId"
        element={
          <ProtectedRoute>
            <AgentEdit />
          </ProtectedRoute>
        }
      />
      <Route
        path="/manage-keys"
        element={
          <ProtectedRoute>
            <ManageKeys />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

// Main App Component
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
