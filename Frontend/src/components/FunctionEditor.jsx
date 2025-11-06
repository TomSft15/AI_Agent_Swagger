/**
 * Function Editor Component
 *
 * Allows editing custom descriptions for API functions
 */
import { useState, useEffect } from 'react';
import { Save, RotateCcw, Edit2, Check, X } from 'lucide-react';
import { agentAPI } from '../services/api';
import './FunctionEditor.css';

const FunctionEditor = ({ agentId, availableFunctions }) => {
  const [functionCustomizations, setFunctionCustomizations] = useState({});
  const [editingFunction, setEditingFunction] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCustomizations();
  }, [agentId]);

  const loadCustomizations = async () => {
    try {
      const customizations = await agentAPI.getFunctions(agentId);
      const customizationsMap = {};
      customizations.forEach(c => {
        customizationsMap[c.operation_id] = c;
      });
      setFunctionCustomizations(customizationsMap);
    } catch (err) {
      console.error('[FunctionEditor] Load error:', err);
      // It's ok if there are no customizations yet
      setFunctionCustomizations({});
    }
  };

  const startEdit = (func) => {
    const operationId = func.name;
    const existingCustomization = functionCustomizations[operationId];
    setEditingFunction(operationId);
    setEditValue(existingCustomization?.custom_description || func.description || '');
  };

  const cancelEdit = () => {
    setEditingFunction(null);
    setEditValue('');
    setError('');
  };

  const saveDescription = async (func) => {
    const operationId = func.name;
    try {
      setSaving(true);
      setError('');

      await agentAPI.updateFunction(agentId, operationId, editValue, true);

      // Reload customizations
      await loadCustomizations();

      setEditingFunction(null);
      setEditValue('');
    } catch (err) {
      console.error('[FunctionEditor] Save error:', err);
      setError('Failed to save: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const resetDescription = async (func) => {
    const operationId = func.name;
    if (!window.confirm(`Reset description for "${func.name}" to default?`)) {
      return;
    }

    try {
      setSaving(true);
      setError('');

      await agentAPI.deleteFunction(agentId, operationId);

      // Reload customizations
      await loadCustomizations();
    } catch (err) {
      console.error('[FunctionEditor] Reset error:', err);
      setError('Failed to reset: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!availableFunctions || availableFunctions.length === 0) {
    return (
      <div className="function-editor-empty">
        <p>No functions available for this agent.</p>
      </div>
    );
  }

  return (
    <div className="function-editor">
      <div className="function-editor-header">
        <h3>API Functions</h3>
        <p className="function-editor-subtitle">
          Add custom descriptions to help the LLM better understand and use each function
        </p>
      </div>

      {error && (
        <div className="function-editor-error">
          {error}
        </div>
      )}

      <div className="functions-list">
        {availableFunctions.map((func) => {
          const operationId = func.name;
          const customization = functionCustomizations[operationId];
          const isEditing = editingFunction === operationId;
          const hasCustomDescription = customization?.custom_description;

          return (
            <div key={operationId} className="function-item">
              <div className="function-header">
                <div className="function-method-badge" data-method={func.method?.toLowerCase()}>
                  {func.method}
                </div>
                <div className="function-info">
                  <div className="function-name">{func.name}</div>
                  <div className="function-path">{func.path}</div>
                </div>
                {hasCustomDescription && !isEditing && (
                  <span className="custom-badge">Custom</span>
                )}
              </div>

              <div className="function-description">
                {isEditing ? (
                  <div className="function-edit-mode">
                    <textarea
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      placeholder="Add a custom description to help the LLM understand this function..."
                      className="function-textarea"
                      rows={4}
                    />
                    <div className="function-edit-actions">
                      <button
                        onClick={() => saveDescription(func)}
                        disabled={saving}
                        className="btn-save"
                      >
                        <Check size={16} />
                        {saving ? 'Saving...' : 'Save'}
                      </button>
                      <button
                        onClick={cancelEdit}
                        disabled={saving}
                        className="btn-cancel"
                      >
                        <X size={16} />
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="function-desc-text">
                      {hasCustomDescription ? (
                        <>
                          <strong>Custom:</strong> {customization.custom_description}
                          {func.description && (
                            <div className="function-original-desc">
                              <strong>Original:</strong> {func.description}
                            </div>
                          )}
                        </>
                      ) : (
                        func.description || <em className="no-description">No description</em>
                      )}
                    </div>
                    <div className="function-actions">
                      <button
                        onClick={() => startEdit(func)}
                        className="btn-edit"
                        title="Edit custom description"
                      >
                        <Edit2 size={16} />
                        {hasCustomDescription ? 'Edit' : 'Add Description'}
                      </button>
                      {hasCustomDescription && (
                        <button
                          onClick={() => resetDescription(func)}
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
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FunctionEditor;
