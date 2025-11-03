/**
 * Swagger View Page
 *
 * View details of a Swagger document
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, FileText, Globe, Calendar, Code } from 'lucide-react';
import { swaggerAPI } from '../services/api';
import './SwaggerView.css';

const SwaggerView = () => {
  const navigate = useNavigate();
  const { swaggerId } = useParams();
  const [swagger, setSwagger] = useState(null);
  const [endpoints, setEndpoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const fetchSwaggerData = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch swagger doc and endpoints in parallel
        const [swaggerResponse, endpointsResponse] = await Promise.all([
          swaggerAPI.getById(swaggerId),
          swaggerAPI.getEndpoints(swaggerId)
        ]);

        console.log('[SwaggerView] Swagger data:', swaggerResponse);
        console.log('[SwaggerView] Endpoints:', endpointsResponse);

        if (isMounted) {
          setSwagger(swaggerResponse);
          // Handle different response formats
          const endpointsList = Array.isArray(endpointsResponse)
            ? endpointsResponse
            : (endpointsResponse.items || []);
          setEndpoints(endpointsList);
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
          <button onClick={() => navigate('/agentManager')} className="back-button">
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
          <button onClick={() => navigate('/agentManager')} className="back-button">
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

        {/* Endpoints List */}
        {endpoints && endpoints.length > 0 && (
          <div className="endpoints-card">
            <h2>API Endpoints ({endpoints.length})</h2>
            <div className="endpoints-list">
              {endpoints.map((endpoint, index) => (
                <div key={index} className="endpoint-item">
                  <div className="endpoint-header">
                    <span className={`method-badge method-${endpoint.method.toLowerCase()}`}>
                      {endpoint.method}
                    </span>
                    <code className="endpoint-path">{endpoint.path}</code>
                  </div>
                  {endpoint.summary && (
                    <p className="endpoint-summary">{endpoint.summary}</p>
                  )}
                  {endpoint.description && (
                    <p className="endpoint-description">{endpoint.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="actions-card">
          <button
            onClick={() => navigate('/agentManager')}
            className="action-button primary"
          >
            Back to Agents
          </button>
        </div>
      </div>
    </div>
  );
};

export default SwaggerView;
