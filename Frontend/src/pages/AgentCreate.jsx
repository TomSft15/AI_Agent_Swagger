/**
 * Agent Create Page
 *
 * Create new AI agent with Swagger upload
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, Bot, X, Check } from 'lucide-react';
import { swaggerAPI, agentAPI } from '../services/api';
import './AgentCreate.css';

const AgentCreate = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: Swagger, 2: Agent config
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Swagger upload state
  const [swaggerData, setSwaggerData] = useState({
    file: null,
    name: '',
    description: '',
    base_url: '',
  });
  const [uploadedSwagger, setUploadedSwagger] = useState(null);

  // Agent config state
  const [agentData, setAgentData] = useState({
    name: '',
    description: '',
    llm_provider: 'openai',
    llm_model: 'gpt-4-turbo-preview',
    temperature: 70,
    max_tokens: 4096,
  });

  // Handle swagger file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSwaggerData({
        ...swaggerData,
        file: file,
        name: swaggerData.name || file.name.replace(/\.(json|yaml|yml)$/, ''),
      });
      setError('');
    }
  };

  // Handle swagger form input
  const handleSwaggerInputChange = (e) => {
    setSwaggerData({
      ...swaggerData,
      [e.target.name]: e.target.value,
    });
  };

  // Handle agent form input
  const handleAgentInputChange = (e) => {
    const { name, value } = e.target;
    setAgentData({
      ...agentData,
      [name]: value,
    });
  };

  // Upload Swagger
  const handleSwaggerUpload = async (e) => {
    e.preventDefault();

    if (!swaggerData.file) {
      setError('Please select a file');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const result = await swaggerAPI.upload(
        swaggerData.file,
        swaggerData.name,
        swaggerData.description,
        swaggerData.base_url
      );

      console.log('[AgentCreate] Swagger uploaded:', result);
      setUploadedSwagger(result.swagger_doc || result);
      setSuccess('Swagger document uploaded successfully!');

      // Pre-fill agent name if not set
      if (!agentData.name) {
        setAgentData({
          ...agentData,
          name: swaggerData.name + ' Agent',
        });
      }

      // Move to next step
      setTimeout(() => {
        setStep(2);
        setSuccess('');
      }, 1000);
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Create Agent
  const handleAgentCreate = async (e) => {
    e.preventDefault();

    if (!uploadedSwagger) {
      setError('Please upload a Swagger document first');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const createData = {
        swagger_doc_id: uploadedSwagger.id,
        name: agentData.name,
        description: agentData.description || null,
        llm_provider: agentData.llm_provider,
        llm_model: agentData.llm_model,
        temperature: parseInt(agentData.temperature),
        max_tokens: parseInt(agentData.max_tokens),
      };

      const result = await agentAPI.create(createData);
      console.log('[AgentCreate] Agent created:', result);

      setSuccess('Agent created successfully!');

      // Redirect to agent manager
      setTimeout(() => {
        navigate('/agentManager');
      }, 1500);
    } catch (err) {
      setError('Failed to create agent: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="agent-create">
      <div className="create-header">
        <div className="header-content">
          <button onClick={() => navigate('/agentManager')} className="back-button">
            <ArrowLeft size={20} />
            Back to Agents
          </button>
          <h1>Create New Agent</h1>
          <p>Upload your API documentation and configure your AI agent</p>
        </div>
      </div>

      <div className="create-content">
        {/* Steps Indicator */}
        <div className="steps-indicator">
          <div className={`step ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
            <div className="step-number">1</div>
            <div className="step-label">Upload Swagger</div>
          </div>
          <div className="step-line"></div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>
            <div className="step-number">2</div>
            <div className="step-label">Configure Agent</div>
          </div>
        </div>

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

        {/* Step 1: Swagger Upload */}
        {step === 1 && (
          <div className="create-section">
            <div className="section-header">
              <Upload size={24} />
              <h2>Upload Swagger/OpenAPI Document</h2>
            </div>

            <form onSubmit={handleSwaggerUpload} className="create-form">
              <div className="form-group">
                <label htmlFor="file-input">
                  Swagger/OpenAPI File * <span className="file-hint">(JSON or YAML)</span>
                </label>
                <input
                  type="file"
                  id="file-input"
                  accept=".json,.yaml,.yml"
                  onChange={handleFileChange}
                  required
                />
                {swaggerData.file && (
                  <div className="file-selected">
                    <FileText size={16} />
                    {swaggerData.file.name}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="swagger-name">API Name *</label>
                <input
                  type="text"
                  id="swagger-name"
                  name="name"
                  value={swaggerData.name}
                  onChange={handleSwaggerInputChange}
                  placeholder="My API"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="swagger-description">API Description</label>
                <textarea
                  id="swagger-description"
                  name="description"
                  value={swaggerData.description}
                  onChange={handleSwaggerInputChange}
                  placeholder="Description of your API"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label htmlFor="base-url">
                  Base URL *<span className="file-hint">(https://api.example.com)</span>
                </label>
                <input
                  type="text"
                  id="base-url"
                  name="base_url"
                  value={swaggerData.base_url}
                  onChange={handleSwaggerInputChange}
                  placeholder="https://api.example.com"
                  required
                />
                <small>Override the base URL from the Swagger file.</small>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => navigate('/agentManager')}
                  className="cancel-button"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="next-button"
                  disabled={loading || !swaggerData.file}
                >
                  <Upload size={18} />
                  {loading ? 'Uploading...' : 'Upload & Continue'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: Agent Configuration */}
        {step === 2 && uploadedSwagger && (
          <div className="create-section">
            <div className="section-header">
              <Bot size={24} />
              <h2>Configure Your Agent</h2>
            </div>

            <div className="swagger-info">
              <FileText size={18} />
              <div>
                <strong>{uploadedSwagger.name}</strong>
                <span>{uploadedSwagger.endpoints_count || 0} endpoints loaded</span>
              </div>
            </div>

            <form onSubmit={handleAgentCreate} className="create-form">
              <div className="form-group">
                <label htmlFor="agent-name">Agent Name *</label>
                <input
                  type="text"
                  id="agent-name"
                  name="name"
                  value={agentData.name}
                  onChange={handleAgentInputChange}
                  placeholder="My API Agent"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="agent-description">Agent Description</label>
                <textarea
                  id="agent-description"
                  name="description"
                  value={agentData.description}
                  onChange={handleAgentInputChange}
                  placeholder="What does this agent do?"
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="llm_provider">LLM Provider *</label>
                  <select
                    id="llm_provider"
                    name="llm_provider"
                    value={agentData.llm_provider}
                    onChange={handleAgentInputChange}
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
                    value={agentData.llm_model}
                    onChange={handleAgentInputChange}
                    placeholder="gpt-4-turbo-preview"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="temperature">
                    Temperature: {agentData.temperature}
                  </label>
                  <input
                    type="range"
                    id="temperature"
                    name="temperature"
                    min="0"
                    max="100"
                    value={agentData.temperature}
                    onChange={handleAgentInputChange}
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
                    value={agentData.max_tokens}
                    onChange={handleAgentInputChange}
                    required
                  />
                  <small>Maximum response length</small>
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="back-button-form"
                  disabled={loading}
                >
                  <ArrowLeft size={18} />
                  Back
                </button>
                <button
                  type="submit"
                  className="create-button"
                  disabled={loading}
                >
                  <Bot size={18} />
                  {loading ? 'Creating...' : 'Create Agent'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentCreate;
