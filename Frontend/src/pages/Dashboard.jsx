/**
 * Dashboard Page
 *
 * Main page after login - displays user info and navigation
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AgentSelectionModal from '../components/AgentSelectionModal';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showAgentModal, setShowAgentModal] = useState(false);

  const handleSelectAgent = (agent) => {
    navigate(`/chat/${agent.id}`, { state: { agentId: agent.id } });
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>AI Agent Platform</h1>
          <div className="user-info">
            <span className="user-email">{user?.email}</span>
            <button onClick={logout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="welcome-card">
          <h2>Welcome, {user?.full_name || user?.username || 'User'}!</h2>
          <p>You are successfully logged in to the AI Agent Platform.</p>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <div className="card-icon">🤖</div>
            <h3>AI Agents</h3>
            <p>Create and configure AI agents from your APIs</p>
            <button className="card-button" onClick={() => navigate('/agent-manager')}>
              Manage Agents
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">💬</div>
            <h3>Chat</h3>
            <p>Interact with your AI agents through conversations</p>
            <button className="card-button" onClick={() => setShowAgentModal(true)}>Start Chat</button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🔑</div>
            <h3>API Keys</h3>
            <p>Configure your LLM provider API keys</p>
            <button className="card-button" onClick={() => navigate('/manage-keys')}>Manage Keys</button>
          </div>
        </div>

        <div className="info-section">
          <h3>Getting Started</h3>
          <ol>
            <li>Go to Manage Agents and create a new AI agent</li>
            <li>Upload a Swagger/OpenAPI specification document for your API</li>
            <li>Configure your LLM provider (OpenAI, Anthropic, or Ollama)</li>
            <li>Start chatting with your agent to interact with your APIs</li>
          </ol>
        </div>
      </main>

      <AgentSelectionModal
        isOpen={showAgentModal}
        onClose={() => setShowAgentModal(false)}
        onSelectAgent={handleSelectAgent}
      />
    </div>
  );
};

export default Dashboard;
