/**
 * Swagger View Page
 *
 * View details of a Swagger document
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, FileText, Globe, Calendar, Code, RefreshCw } from 'lucide-react';
import { swaggerAPI, agentAPI } from '../services/api';
import FunctionEditor from '../components/FunctionEditor';
import './SwaggerView.css';

const SwaggerView = () => {
  const navigate = useNavigate();
  const { swaggerId } = useParams();
  const functionEditorRef = useRef();
  const [swagger, setSwagger] = useState(null);
  const [endpoints, setEndpoints] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const fetchSwaggerData = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch swagger doc, endpoints, and agents in parallel
        const [swaggerResponse, endpointsResponse, agentsResponse] = await Promise.all([
          swaggerAPI.getById(swaggerId),
          swaggerAPI.getEndpoints(swaggerId),
          agentAPI.getAll()
        ]);

        console.log('[SwaggerView] Swagger data:', swaggerResponse);
        console.log('[SwaggerView] Endpoints:', endpointsResponse);
        console.log('[SwaggerView] Agents:', agentsResponse);

        if (isMounted) {
          setSwagger(swaggerResponse);
          // Handle different response formats
          const endpointsList = Array.isArray(endpointsResponse)
            ? endpointsResponse
            : (endpointsResponse.items || []);
          setEndpoints(endpointsList);

          // Filter agents that use this swagger doc
          const agentsList = Array.isArray(agentsResponse)
            ? agentsResponse
            : (agentsResponse.items || []);
          const relatedAgents = agentsList.filter(agent => agent.swagger_doc_id === parseInt(swaggerId));
          setAgents(relatedAgents);
        }
      } catch (err) {
        console.error('[SwaggerView] Load error:', err);
        if (isMounted) {
          setError('Failed to load Swagger document: ' + err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchSwaggerData();

    return () => {
      isMounted = false;
    };
  }, [swaggerId]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const handleSaveAndRegenerate = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      // Save all customizations
      if (functionEditorRef.current) {
        await functionEditorRef.current.saveAllChanges();
      }

      // Regenerate all agents using this swagger doc
      const regeneratePromises = agents.map(agent =>
        agentAPI.regenerate(agent.id)
      );

      await Promise.all(regeneratePromises);

      setSuccess(`Successfully saved customizations and regenerated ${agents.length} agent(s)!`);
      setHasChanges(false);

      // Refresh page data after a short delay
      setTimeout(() => {
        window.location.reload();
      }, 2000);

    } catch (err) {
      console.error('[SwaggerView] Save and regenerate error:', err);
      setError('Failed to save and regenerate: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="swagger-view">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading Swagger document...</p>
        </div>
      </div>
    );
  }

  if (error || !swagger) {
    return (
      <div className="swagger-view">
        <div className="error-container">
          <p>{error || 'Swagger document not found'}</p>
          <button onClick={() => navigate('/agent-manager')} className="back-button">
            Back to Agents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="swagger-view">
      <div className="view-header">
        <div className="header-content">
          <button onClick={() => navigate('/agent-manager')} className="back-button">
            <ArrowLeft size={20} />
            Back to Agents
          </button>
          <div className="title-section">
            <FileText size={40} />
            <div>
              <h1>{swagger.name}</h1>
              {swagger.description && <p>{swagger.description}</p>}
            </div>
          </div>
        </div>
      </div>

      <div className="view-content">
        {/* Alerts */}
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            {success}
          </div>
        )}

        {/* Basic Information */}
        <div className="info-card">
          <h2>Document Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">
                <Calendar size={16} />
                Created
              </span>
              <span className="info-value">{formatDate(swagger.created_at)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">
                <Code size={16} />
                Version
              </span>
              <span className="info-value">{swagger.version || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">
                <Globe size={16} />
                Base URL
              </span>
              <span className="info-value">
                {swagger.base_url || 'Not specified'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">
                <FileText size={16} />
                Endpoints
              </span>
              <span className="info-value">{swagger.endpoints_count || 0}</span>
            </div>
          </div>
        </div>

        {/* Function Editor for endpoint customizations */}
        {endpoints && endpoints.length > 0 && (
          <FunctionEditor
            ref={functionEditorRef}
            swaggerId={parseInt(swaggerId)}
            endpoints={endpoints}
            onHasChanges={setHasChanges}
          />
        )}

        {/* Actions */}
        <div className="actions-card">
          {agents.length > 0 && (
            <div className="agents-info">
              <p>
                <strong>{agents.length}</strong> agent{agents.length !== 1 ? 's' : ''} using this API
              </p>
            </div>
          )}

          <div className="action-buttons">
            <button
              onClick={() => navigate('/agent-manager')}
              className="action-button secondary"
            >
              <ArrowLeft size={18} />
              Back to Agents
            </button>

            {agents.length > 0 && (
              <button
                onClick={handleSaveAndRegenerate}
                disabled={saving || !hasChanges}
                className={`action-button primary ${hasChanges ? 'has-changes' : ''}`}
                title={hasChanges ? `Save changes and regenerate ${agents.length} agent(s)` : 'No changes to save'}
              >
                <RefreshCw size={18} className={saving ? 'spinning' : ''} />
                {saving ? 'Saving & Regenerating...' : 'Save & Regenerate Agents'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SwaggerView;
