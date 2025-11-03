/**
 * Swagger Management Page
 *
 * Upload and manage OpenAPI/Swagger documents
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Trash2, Calendar, Check, X, ArrowLeft } from 'lucide-react';
import { swaggerAPI } from '../services/api';
import './SwaggerManagement.css';

const SwaggerManagement = () => {
  const navigate = useNavigate();
  console.log('[SwaggerManagement] Component rendering...');
  const [swaggerDocs, setSwaggerDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Upload form state
  const [uploadData, setUploadData] = useState({
    file: null,
    name: '',
    description: '',
  });

  useEffect(() => {
    let isMounted = true;

    const fetchSwaggerDocs = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await swaggerAPI.getAll();
        console.log('[SwaggerManagement] API response:', response);

        // Handle different response formats
        const docs = Array.isArray(response) ? response : (response.items || response.data || []);
        console.log('[SwaggerManagement] Swagger docs:', docs);

        if (isMounted) {
          setSwaggerDocs(docs);
        }
      } catch (err) {
        console.error('[SwaggerManagement] Load error:', err);
        if (isMounted) {
          setError('Failed to load Swagger documents: ' + err.message);
          setSwaggerDocs([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchSwaggerDocs();

    return () => {
      isMounted = false;
    };
  }, []);

  const loadSwaggerDocs = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await swaggerAPI.getAll();
      console.log('[SwaggerManagement] API response:', response);

      // Handle different response formats
      const docs = Array.isArray(response) ? response : (response.items || response.data || []);
      console.log('[SwaggerManagement] Swagger docs:', docs);

      setSwaggerDocs(docs);
    } catch (err) {
      console.error('[SwaggerManagement] Load error:', err);
      setError('Failed to load Swagger documents: ' + err.message);
      setSwaggerDocs([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadData({
        ...uploadData,
        file: file,
        name: uploadData.name || file.name.replace(/\.(json|yaml|yml)$/, ''),
      });
      setError('');
      setSuccess('');
    }
  };

  const handleInputChange = (e) => {
    setUploadData({
      ...uploadData,
      [e.target.name]: e.target.value,
    });
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!uploadData.file) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setError('');
      setSuccess('');

      await swaggerAPI.upload(
        uploadData.file,
        uploadData.name,
        uploadData.description
      );

      setSuccess('Swagger document uploaded successfully!');

      // Reset form
      setUploadData({
        file: null,
        name: '',
        description: '',
      });

      // Reset file input
      document.getElementById('file-input').value = '';

      // Reload list
      await loadSwaggerDocs();
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      setError('');
      await swaggerAPI.delete(id);
      setSuccess(`"${name}" deleted successfully`);
      await loadSwaggerDocs();
    } catch (err) {
      setError('Delete failed: ' + err.message);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="swagger-management">
      <div className="swagger-header">
        <div className="header-content">
          <button onClick={() => navigate('/')} className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h1>Swagger Documents</h1>
          <p>Upload and manage your OpenAPI/Swagger specifications</p>
        </div>
      </div>

      <div className="swagger-content">
        {/* Upload Section */}
        <div className="upload-section">
          <div className="section-header">
            <Upload size={24} />
            <h2>Upload New Document</h2>
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

          <form onSubmit={handleUpload} className="upload-form">
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
              {uploadData.file && (
                <div className="file-selected">
                  <FileText size={16} />
                  {uploadData.file.name}
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="name">Document Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={uploadData.name}
                onChange={handleInputChange}
                placeholder="My API"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description (optional)</label>
              <textarea
                id="description"
                name="description"
                value={uploadData.description}
                onChange={handleInputChange}
                placeholder="Description of your API"
                rows="3"
              />
            </div>

            <button
              type="submit"
              className="upload-button"
              disabled={uploading || !uploadData.file}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </form>
        </div>

        {/* Documents List */}
        <div className="documents-section">
          <div className="section-header">
            <FileText size={24} />
            <h2>Your Documents</h2>
          </div>

          {loading ? (
            <div className="loading">Loading documents...</div>
          ) : !Array.isArray(swaggerDocs) || swaggerDocs.length === 0 ? (
            <div className="empty-state">
              <FileText size={48} />
              <p>No Swagger documents yet</p>
              <p className="empty-hint">Upload your first OpenAPI/Swagger file to get started</p>
            </div>
          ) : (
            <div className="documents-list">
              {swaggerDocs.map((doc) => (
                <div key={doc.id} className="document-card">
                  <div className="document-icon">
                    <FileText size={32} />
                  </div>
                  <div className="document-info">
                    <h3>{doc.name}</h3>
                    {doc.description && <p className="document-description">{doc.description}</p>}
                    <div className="document-meta">
                      <span className="meta-item">
                        <Calendar size={14} />
                        {formatDate(doc.created_at)}
                      </span>
                      <span className="meta-item">
                        Version: {doc.version || 'N/A'}
                      </span>
                      <span className="meta-item">
                        {doc.endpoints_count || 0} endpoints
                      </span>
                    </div>
                    {doc.base_url && (
                      <div className="document-url">
                        <strong>Base URL:</strong> {doc.base_url}
                      </div>
                    )}
                  </div>
                  <div className="document-actions">
                    <button
                      onClick={() => handleDelete(doc.id, doc.name)}
                      className="delete-button"
                      title="Delete document"
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

export default SwaggerManagement;
