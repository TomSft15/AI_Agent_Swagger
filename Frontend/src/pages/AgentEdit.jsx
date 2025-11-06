/**
 * Agent Edit Page
 *
 * Edit AI agent configuration
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Bot, X, Check } from 'lucide-react';
import { agentAPI } from '../services/api';
import FunctionEditor from '../components/FunctionEditor';
import './AgentEdit.css';

const AgentEdit = () => {
  const navigate = useNavigate();
  const { agentId } = useParams();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [agent, setAgent] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    llm_provider: '',
    llm_model: '',
    temperature: 70,
    max_tokens: 4096,
    is_active: true,
  });

  useEffect(() => {
    let isMounted = true;

    const fetchAgent = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await agentAPI.getById(agentId);
        console.log('[AgentEdit] Agent data:', response);

        if (isMounted) {
          setAgent(response);
          setFormData({
            name: response.name || '',
            description: response.description || '',
            llm_provider: response.llm_provider || '',
            llm_model: response.llm_model || '',
            temperature: response.temperature || 70,
            max_tokens: response.max_tokens || 4096,
            is_active: response.is_active ?? true,
            swagger_doc_name: response.swagger_doc_name || '',
          });
        }
      } catch (err) {
        console.error('[AgentEdit] Load error:', err);
        if (isMounted) {
          setError('Failed to load agent: ' + err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchAgent();

    return () => {
      isMounted = false;
    };
  }, [agentId]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const updateData = {
        name: formData.name,
        description: formData.description || null,
        llm_provider: formData.llm_provider,
        llm_model: formData.llm_model,
        temperature: parseInt(formData.temperature),
        max_tokens: parseInt(formData.max_tokens),
        is_active: formData.is_active,
      };

      await agentAPI.update(agentId, updateData);
      setSuccess('Agent updated successfully!');

      // Redirect after 1 second
      setTimeout(() => {
        navigate('/agent-manager');
      }, 1000);
    } catch (err) {
      setError('Update failed: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="agent-edit">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading agent...</p>
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="agent-edit">
        <div className="error-container">
          <p>Agent not found</p>
          <button onClick={() => navigate('/agent-manager')} className="back-button">
            Back to Agents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="agent-edit">
      <div className="edit-header">
        <div className="header-content">
          <button onClick={() => navigate('/agent-manager')} className="back-button">
            <ArrowLeft size={20} />
            Back to Agents
          </button>
          <h1>Edit Agent</h1>
          <p>Configure your AI agent settings</p>
        </div>
      </div>

      <div className="edit-content">
        {error && (
          <div className="alert alert-error">
            <X size={20} />
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <Check size={20} />
            {success}
          </div>
        )}

        <div className="edit-section">
          <div className="section-header">
            <Bot size={24} />
            <h2>Agent Configuration</h2>
          </div>

          <form onSubmit={handleSubmit} className="edit-form">
            {/* Basic Information */}
            <div className="form-section">
              <h3>Basic Information</h3>

              <div className="form-group">
                <label htmlFor="name">Agent Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="My API Agent"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Description of your agent"
                  rows="3"
                />
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                  />
                  <span>Active</span>
                </label>
                <small>Inactive agents cannot be used for chat</small>
              </div>
            </div>

            {/* LLM Configuration */}
            <div className="form-section">
              <h3>LLM Configuration</h3>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="llm_provider">LLM Provider *</label>
                  <select
                    id="llm_provider"
                    name="llm_provider"
                    value={formData.llm_provider}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="openai">OpenAI</option>
                    <option value="ollama">Ollama</option>
                    <option value="mistral">Mistral</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="llm_model">Model *</label>
                  <input
                    type="text"
                    id="llm_model"
                    name="llm_model"
                    value={formData.llm_model}
                    onChange={handleInputChange}
                    placeholder="gpt-4-turbo-preview"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="temperature">
                    Temperature: {formData.temperature}
                  </label>
                  <input
                    type="range"
                    id="temperature"
                    name="temperature"
                    min="0"
                    max="100"
                    value={formData.temperature}
                    onChange={handleInputChange}
                  />
                  <small>Lower = more focused, Higher = more creative</small>
                </div>

                <div className="form-group">
                  <label htmlFor="max_tokens">Max Tokens *</label>
                  <input
                    type="number"
                    id="max_tokens"
                    name="max_tokens"
                    min="1"
                    max="128000"
                    value={formData.max_tokens}
                    onChange={handleInputChange}
                    required
                  />
                  <small>Maximum response length</small>
                </div>
              </div>
            </div>

            {/* Agent Info (Read-only) */}
            <div className="form-section info-section">
              <h3>Agent Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Swagger Document:</span>
                  <span className="info-value">{agent.swagger_doc_name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Functions:</span>
                  <span className="info-value">{agent.available_functions?.length || 0}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Created:</span>
                  <span className="info-value">
                    {new Date(agent.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="info-item">
                  <span className="info-label">Last Updated:</span>
                  <span className="info-value">
                    {new Date(agent.updated_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="form-actions">
              <button
                type="button"
                onClick={() => navigate('/agent-manager')}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="save-button"
                disabled={saving}
              >
                <Save size={18} />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>

        {/* Function Editor Section */}
        <FunctionEditor
          agentId={parseInt(agentId)}
          availableFunctions={agent.available_functions || []}
        />
      </div>
    </div>
  );
};

export default AgentEdit;
