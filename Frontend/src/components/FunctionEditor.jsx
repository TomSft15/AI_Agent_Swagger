/**
 * Function Editor Component
 *
 * Allows editing custom descriptions for API endpoints
 * Changes are kept in local state until saved
 */
import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { RotateCcw, Edit2, Check, X } from 'lucide-react';
import { swaggerAPI } from '../services/api';
import './FunctionEditor.css';

const FunctionEditor = forwardRef(({ swaggerId, endpoints, onHasChanges }, ref) => {
  const [savedCustomizations, setSavedCustomizations] = useState({});
  const [localCustomizations, setLocalCustomizations] = useState({});
  const [editingEndpoint, setEditingEndpoint] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadCustomizations();
  }, [swaggerId]);

  // Notify parent when there are unsaved changes
  useEffect(() => {
    const hasChanges = JSON.stringify(savedCustomizations) !== JSON.stringify(localCustomizations);
    if (onHasChanges) {
      onHasChanges(hasChanges);
    }
  }, [savedCustomizations, localCustomizations, onHasChanges]);

  const loadCustomizations = async () => {
    try {
      const customizations = await swaggerAPI.getCustomizations(swaggerId);
      const customizationsMap = {};
      customizations.forEach(c => {
        customizationsMap[c.operation_id] = c;
      });
      setSavedCustomizations(customizationsMap);
      setLocalCustomizations(customizationsMap);
    } catch (err) {
      console.error('[FunctionEditor] Load error:', err);
      // It's ok if there are no customizations yet
      setSavedCustomizations({});
      setLocalCustomizations({});
    }
  };

  const startEdit = (endpoint) => {
    const operationId = endpoint.operation_id;
    const existingCustomization = localCustomizations[operationId];
    setEditingEndpoint(operationId);
    setEditValue(existingCustomization?.custom_description || endpoint.description || '');
  };

  const cancelEdit = () => {
    setEditingEndpoint(null);
    setEditValue('');
    setError('');
  };

  const saveDescriptionLocal = (endpoint) => {
    const operationId = endpoint.operation_id;
    const existing = localCustomizations[operationId];

    // Update local state only
    setLocalCustomizations({
      ...localCustomizations,
      [operationId]: {
        ...existing,
        operation_id: operationId,
        method: endpoint.method,
        path: endpoint.path,
        custom_description: editValue,
        is_enabled: existing?.is_enabled ?? true
      }
    });

    setEditingEndpoint(null);
    setEditValue('');
  };

  const toggleEnabledLocal = (endpoint) => {
    const operationId = endpoint.operation_id;
    const existing = localCustomizations[operationId];
    const currentEnabled = existing?.is_enabled ?? true;

    // Update local state only
    setLocalCustomizations({
      ...localCustomizations,
      [operationId]: {
        ...existing,
        operation_id: operationId,
        method: endpoint.method,
        path: endpoint.path,
        custom_description: existing?.custom_description || null,
        is_enabled: !currentEnabled
      }
    });
  };

  const resetDescriptionLocal = (endpoint) => {
    const operationId = endpoint.operation_id;
    if (!window.confirm(`Reset description for "${endpoint.summary || endpoint.path}" to default?`)) {
      return;
    }

    // Remove from local customizations
    const newCustomizations = { ...localCustomizations };
    if (newCustomizations[operationId]) {
      delete newCustomizations[operationId].custom_description;
      // If no other customizations, remove entirely
      if (!newCustomizations[operationId].is_enabled && newCustomizations[operationId].is_enabled !== false) {
        delete newCustomizations[operationId];
      }
    }
    setLocalCustomizations(newCustomizations);
  };

  // Expose method to save all changes
  const saveAllChanges = async () => {
    const errors = [];

    for (const [operationId, customization] of Object.entries(localCustomizations)) {
      try {
        await swaggerAPI.updateCustomization(
          swaggerId,
          operationId,
          customization.custom_description,
          customization.is_enabled
        );
      } catch (err) {
        console.error(`[FunctionEditor] Failed to save ${operationId}:`, err);
        errors.push(`${operationId}: ${err.message}`);
      }
    }

    // Delete customizations that were removed
    for (const [operationId] of Object.entries(savedCustomizations)) {
      if (!localCustomizations[operationId]) {
        try {
          await swaggerAPI.deleteCustomization(swaggerId, operationId);
        } catch (err) {
          console.error(`[FunctionEditor] Failed to delete ${operationId}:`, err);
          errors.push(`${operationId}: ${err.message}`);
        }
      }
    }

    if (errors.length > 0) {
      throw new Error(`Failed to save some customizations:\n${errors.join('\n')}`);
    }

    // Reload to sync
    await loadCustomizations();
  };

  // Expose saveAllChanges to parent via ref
  useImperativeHandle(ref, () => ({
    saveAllChanges,
    hasChanges: () => JSON.stringify(savedCustomizations) !== JSON.stringify(localCustomizations)
  }));

  if (!endpoints || endpoints.length === 0) {
    return (
      <div className="function-editor-empty">
        <p>No endpoints available for this Swagger document.</p>
      </div>
    );
  }

  return (
    <div className="function-editor">
      <div className="function-editor-header">
        <h3>Endpoint Customizations</h3>
        <p className="function-editor-subtitle">
          Add custom descriptions to help the LLM better understand and use each endpoint
        </p>
      </div>

      {error && (
        <div className="function-editor-error">
          {error}
        </div>
      )}

      <div className="functions-list">
        {endpoints.map((endpoint, index) => {
          const operationId = endpoint.operation_id;
          const customization = localCustomizations[operationId];
          const isEditing = editingEndpoint === operationId;
          const hasCustomDescription = customization?.custom_description;
          const isEnabled = customization?.is_enabled ?? true;

          return (
            <div key={index} className={`function-item ${!isEnabled ? 'disabled' : ''}`}>
              {isEditing ? (
                <>
                  <div className="endpoint-header">
                    <span className={`method-badge method-${endpoint.method?.toLowerCase()}`}>
                      {endpoint.method}
                    </span>
                    <code className="endpoint-path">{endpoint.path}</code>
                  </div>

                  <div className="function-edit-mode">
                    <label className="edit-label">Custom Description</label>
                    <textarea
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      placeholder="Add a custom description to help the LLM understand this endpoint..."
                      className="function-textarea"
                      rows={4}
                    />
                    <div className="function-edit-actions">
                      <button
                        onClick={() => saveDescriptionLocal(endpoint)}
                        className="btn-save"
                      >
                        <Check size={16} />
                        Apply
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="btn-cancel"
                      >
                        <X size={16} />
                        Cancel
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="endpoint-header">
                    <div className="endpoint-header-left">
                      <span className={`method-badge method-${endpoint.method?.toLowerCase()}`}>
                        {endpoint.method}
                      </span>
                      <code className="endpoint-path">{endpoint.path}</code>
                      {hasCustomDescription && (
                        <span className="custom-badge">Custom</span>
                      )}
                      {!isEnabled && (
                        <span className="disabled-badge">Disabled</span>
                      )}
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={isEnabled}
                        onChange={() => toggleEnabledLocal(endpoint)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  {endpoint.summary && (
                    <p className="endpoint-summary">{endpoint.summary}</p>
                  )}

                  {hasCustomDescription ? (
                    <>
                      <div className="custom-description">
                        <span className="description-label">Custom Description:</span>
                        <p className="endpoint-description custom">{customization.custom_description}</p>
                      </div>
                      {endpoint.description && (
                        <div className="original-description">
                          <span className="description-label">Original Description:</span>
                          <p className="endpoint-description">{endpoint.description}</p>
                        </div>
                      )}
                    </>
                  ) : (
                    endpoint.description && (
                      <p className="endpoint-description">{endpoint.description}</p>
                    )
                  )}

                  <div className="function-actions">
                    <button
                      onClick={() => startEdit(endpoint)}
                      className="btn-edit"
                      title="Edit custom description"
                    >
                      <Edit2 size={16} />
                      {hasCustomDescription ? 'Edit Custom Description' : 'Add Custom Description'}
                    </button>
                    {hasCustomDescription && (
                      <button
                        onClick={() => resetDescriptionLocal(endpoint)}
                        className="btn-reset"
                        title="Reset to default"
                      >
                        <RotateCcw size={16} />
                        Reset
                      </button>
                    )}
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
});

FunctionEditor.displayName = 'FunctionEditor';

export default FunctionEditor;
