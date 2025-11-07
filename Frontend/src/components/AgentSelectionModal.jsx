/**
 * Agent Selection Modal Component
 *
 * Modal to select an AI agent before starting a chat
 */
import { useState, useEffect } from 'react';
import { Bot, X, Power, PowerOff } from 'lucide-react';
import { agentAPI } from '../services/api';
import './AgentSelectionModal.css';

const AgentSelectionModal = ({ isOpen, onClose, onSelectAgent }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAgentId, setSelectedAgentId] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadAgents();
    }
  }, [isOpen]);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await agentAPI.getAll();

      // Handle different response formats
      const agentsList = Array.isArray(response) ? response : (response.items || response.data || []);

      // Filter only active agents
      const activeAgents = agentsList.filter(agent => agent.is_active);

      if (activeAgents.length === 0) {
        setError('No active agents available. Please activate an agent first.');
      }

      setAgents(activeAgents);
    } catch (err) {
      console.error('[AgentSelectionModal] Load error:', err);
      setError('Failed to load agents: ' + err.message);
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAgent = () => {
    if (selectedAgentId) {
      const agent = agents.find(a => a.id === selectedAgentId);
      onSelectAgent(agent);
      onClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select an Agent</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="modal-loading">Loading agents...</div>
          ) : error ? (
            <div className="modal-error">{error}</div>
          ) : agents.length === 0 ? (
            <div className="modal-empty">
              <Bot size={48} />
              <p>No active agents available</p>
              <p className="empty-hint">Create and activate an agent to start chatting</p>
            </div>
          ) : (
            <div className="agents-grid">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className={`agent-option ${selectedAgentId === agent.id ? 'selected' : ''}`}
                  onClick={() => setSelectedAgentId(agent.id)}
                >
                  <div className="agent-option-icon">
                    <Bot size={24} />
                  </div>
                  <div className="agent-option-info">
                    <div className="agent-option-header">
                      <h3>{agent.name}</h3>
                      {agent.is_active && (
                        <span className="status-badge">
                          <Power size={10} />
                        </span>
                      )}
                    </div>
                    {agent.description && (
                      <p className="agent-option-description">{agent.description}</p>
                    )}
                    <div className="agent-option-meta">
                      {agent.llm_provider}/{agent.llm_model}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="modal-button modal-button-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="modal-button modal-button-primary"
            onClick={handleSelectAgent}
            disabled={!selectedAgentId}
          >
            Start Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentSelectionModal;
