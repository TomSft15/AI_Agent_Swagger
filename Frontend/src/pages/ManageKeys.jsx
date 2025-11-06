/**
 * Manage Keys Page
 *
 * Manage LLM provider API keys
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Key, Eye, EyeOff, Save, AlertCircle } from 'lucide-react';
import { userAPI } from '../services/api';
import './ManageKeys.css';

const ManageKeys = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // API Keys state
  const [keys, setKeys] = useState({
    openai_api_key: '',
    anthropic_api_key: '',
  });

  // Visibility state for each key
  const [visibility, setVisibility] = useState({
    openai_api_key: false,
    anthropic_api_key: false,
  });

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = async () => {
    try {
      setLoading(true);
      setError('');
      const keysData = await userAPI.getKeys();

      // Load existing keys (they might be partially masked)
      setKeys({
        openai_api_key: keysData.openai_api_key_masked || '',
        anthropic_api_key: keysData.anthropic_api_key_masked || '',
      });
    } catch (err) {
      console.error('[ManageKeys] Load error:', err);
      setError('Failed to load API keys: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setKeys(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear messages when user starts typing
    setError('');
    setSuccess('');
  };

  const toggleVisibility = (field) => {
    setVisibility(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      // Only send non-empty keys
      const keysToUpdate = {};
      Object.keys(keys).forEach(key => {
        if (keys[key] && keys[key].trim() !== '') {
          keysToUpdate[key] = keys[key];
        }
      });

      await userAPI.updateKeys(keysToUpdate);
      setSuccess('API keys saved successfully!');

      // Reload keys to get masked versions
      setTimeout(() => {
        loadKeys();
        setSuccess('');
      }, 2000);
    } catch (err) {
      console.error('[ManageKeys] Save error:', err);
      setError('Failed to save API keys: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const providerConfigs = [
    {
      id: 'openai_api_key',
      label: 'OpenAI API Key',
      description: 'Your OpenAI API key for GPT models',
      placeholder: 'sk-...',
      type: 'password',
      icon: '🤖',
      link: 'https://platform.openai.com/api-keys'
    },
    {
      id: 'anthropic_api_key',
      label: 'Anthropic API Key',
      description: 'Your Anthropic API key for Claude models',
      placeholder: 'sk-ant-...',
      type: 'password',
      icon: '🧠',
      link: 'https://console.anthropic.com/settings/keys'
    }
  ];

  return (
    <div className="manage-keys">
      <div className="keys-header">
        <div className="header-content">
          <button onClick={() => navigate('/')} className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h1>API Keys Management</h1>
          <p>Configure your LLM provider API keys</p>
        </div>
      </div>

      <div className="keys-content">
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <Save size={20} />
            {success}
          </div>
        )}

        <div className="keys-section">
          <div className="section-header">
            <div className="header-left">
              <Key size={24} />
              <h2>Provider Keys</h2>
            </div>
          </div>

          {loading ? (
            <div className="loading">Loading keys...</div>
          ) : (
            <div className="keys-list">
              {providerConfigs.map((config) => (
                <div key={config.id} className="key-card">
                  <div className="key-header">
                    <div className="key-icon">{config.icon}</div>
                    <div className="key-info">
                      <h3>{config.label}</h3>
                      <p className="key-description">{config.description}</p>
                      <a
                        href={config.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="key-link"
                      >
                        Get your API key →
                      </a>
                    </div>
                  </div>

                  <div className="key-input-group">
                    <input
                      type={visibility[config.id] ? 'text' : config.type}
                      value={keys[config.id]}
                      onChange={(e) => handleChange(config.id, e.target.value)}
                      placeholder={config.placeholder}
                      className="key-input"
                    />
                    {config.type === 'password' && (
                      <button
                        type="button"
                        onClick={() => toggleVisibility(config.id)}
                        className="visibility-toggle"
                        title={visibility[config.id] ? 'Hide' : 'Show'}
                      >
                        {visibility[config.id] ? (
                          <EyeOff size={18} />
                        ) : (
                          <Eye size={18} />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="keys-actions">
            <button
              onClick={handleSave}
              disabled={saving || loading}
              className="save-button"
            >
              <Save size={18} />
              {saving ? 'Saving...' : 'Save Keys'}
            </button>
          </div>

          <div className="keys-info">
            <h3>Security Information</h3>
            <ul>
              <li>Your API keys are encrypted and stored securely</li>
              <li>Keys are only used to make requests on your behalf</li>
              <li>You can update or remove keys at any time</li>
              <li>Empty fields will not update existing keys</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageKeys;
