/**
 * Agent Manager Page
 *
 * Manage AI agents and their Swagger documents
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, ArrowLeft, Trash2, Calendar, Power, PowerOff, FileText } from 'lucide-react';
import { agentAPI } from '../services/api';
import './AgentManager.css';

const AgentManager = () => {
  const navigate = useNavigate();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const fetchAgents = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await agentAPI.getAll();
        console.log('[AgentManager] API response:', response);

        // Handle different response formats
        const agentsList = Array.isArray(response) ? response : (response.items || response.data || []);
        console.log('[AgentManager] Agents:', agentsList);

        if (isMounted) {
          setAgents(agentsList);
        }
      } catch (err) {
        console.error('[AgentManager] Load error:', err);
        if (isMounted) {
          setError('Failed to load agents: ' + err.message);
          setAgents([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchAgents();

    return () => {
      isMounted = false;
    };
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await agentAPI.getAll();
      console.log('[AgentManager] API response:', response);

      // Handle different response formats
      const agentsList = Array.isArray(response) ? response : (response.items || response.data || []);
      console.log('[AgentManager] Agents:', agentsList);

      setAgents(agentsList);
    } catch (err) {
      console.error('[AgentManager] Load error:', err);
      setError('Failed to load agents: ' + err.message);
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete agent "${name}"?`)) {
      return;
    }

    try {
      setError('');
      await agentAPI.delete(id);
      await loadAgents();
    } catch (err) {
      setError('Delete failed: ' + err.message);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="agent-manager">
      <div className="agent-header">
        <div className="header-content">
          <button onClick={() => navigate('/')} className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h1>AI Agents</h1>
          <p>Manage your AI agents and their configurations</p>
        </div>
      </div>

      <div className="agent-content">
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <div className="agents-section">
          <div className="section-header">
            <div className="header-left">
              <Bot size={24} />
              <h2>Your Agents</h2>
            </div>
            <button
              className="create-button"
              onClick={() => navigate('/agent/create')}
            >
              Create New Agent
            </button>
          </div>

          {loading ? (
            <div className="loading">Loading agents...</div>
          ) : !Array.isArray(agents) || agents.length === 0 ? (
            <div className="empty-state">
              <Bot size={48} />
              <p>No agents yet</p>
              <p className="empty-hint">Create your first AI agent from a Swagger document</p>
              <button
                className="create-button-large"
                onClick={() => navigate('/agent/create')}
              >
                Create Your First Agent
              </button>
            </div>
          ) : (
            <div className="agents-list">
              {agents.map((agent) => (
                <div key={agent.id} className="agent-card">
                  <div className="agent-icon">
                    <Bot size={32} />
                  </div>
                  <div className="agent-info">
                    <div className="agent-header-row">
                      <div className="agent-title">
                        <h3>{agent.name}</h3>
                        {agent.is_active ? (
                          <span className="status-badge status-active">
                            <Power size={12} />
                            Active
                          </span>
                        ) : (
                          <span className="status-badge status-inactive">
                            <PowerOff size={12} />
                            Inactive
                          </span>
                        )}
                      </div>
                    </div>

                    {agent.description && (
                      <p className="agent-description">{agent.description}</p>
                    )}

                    <div className="agent-meta">
                      <span className="meta-item">
                        <Calendar size={14} />
                        {formatDate(agent.created_at)}
                      </span>
                      <span className="meta-item">
                        LLM: {agent.llm_provider}/{agent.llm_model}
                      </span>
                      <span className="meta-item">
                        Functions: {agent.functions_count || 0}
                      </span>
                    </div>

                    {agent.swagger_doc_name && (
                      <div
                        className="agent-swagger clickable"
                        onClick={() => navigate(`/swagger/view/${agent.swagger_doc_id}`)}
                        title="View Swagger document"
                      >
                        <FileText size={14} />
                        <strong>Swagger:</strong> {agent.swagger_doc_name}
                      </div>
                    )}
                  </div>
                  <div className="agent-actions">
                    <button
                      className="action-button action-chat"
                      title="Chat with agent"
                      onClick={() => navigate(`/chat/${agent.id}`, { state: { agentId: agent.id } })}
                    >
                      Chat
                    </button>
                    <button
                      onClick={() => navigate(`/agent/edit/${agent.id}`)}
                      className="action-button action-edit"
                      title="Edit agent"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(agent.id, agent.name)}
                      className="action-button action-delete"
                      title="Delete agent"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentManager;
