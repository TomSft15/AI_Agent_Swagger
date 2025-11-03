/**
 * API Service
 *
 * Handles all HTTP requests to the backend API
 */

// Base URL for the backend API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Make an HTTP request to the API
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  // Get token from localStorage
  const token = localStorage.getItem('access_token');

  // Default headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    console.log(`[API] ${options.method || 'GET'} ${endpoint}`);

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Parse response
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      console.error(`[API] Error ${response.status}:`, data);
      throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    console.log(`[API] Success:`, data);
    return data;

  } catch (error) {
    console.error(`[API] Request failed:`, error);
    throw error;
  }
}

/**
 * Authentication API
 */
export const authAPI = {
  /**
   * Login with email/username and password
   */
  login: async (emailOrUsername, password) => {
    const response = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: emailOrUsername,
        password: password,
      }),
    });

    // Store tokens
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
    }
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }

    return response;
  },

  /**
   * Register new user
   */
  register: async (userData) => {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Logout
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    return apiRequest('/users/me');
  },
};

/**
 * Swagger API
 */
export const swaggerAPI = {
  /**
   * Get all swagger documents
   */
  getAll: async () => {
    return apiRequest('/swagger');
  },

  /**
   * Upload swagger document
   */
  upload: async (file, name, description, base_url) => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    if (description) formData.append('description', description);
    if (base_url) formData.append('base_url', base_url);

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/swagger/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Upload failed');
    }

    return data;
  },

  /**
   * Get swagger document by ID
   */
  getById: async (id) => {
    return apiRequest(`/swagger/${id}`);
  },

  /**
   * Get swagger endpoints
   */
  getEndpoints: async (id) => {
    return apiRequest(`/swagger/${id}/endpoints`);
  },

  /**
   * Delete swagger document
   */
  delete: async (id) => {
    return apiRequest(`/swagger/${id}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Agent API
 */
export const agentAPI = {
  /**
   * Get all agents
   */
  getAll: async () => {
    return apiRequest('/agents');
  },

  /**
   * Create new agent
   */
  create: async (agentData) => {
    return apiRequest('/agents', {
      method: 'POST',
      body: JSON.stringify(agentData),
    });
  },

  /**
   * Get agent by ID
   */
  getById: async (id) => {
    return apiRequest(`/agents/${id}`);
  },

  /**
   * Update agent
   */
  update: async (id, agentData) => {
    return apiRequest(`/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(agentData),
    });
  },

  /**
   * Delete agent
   */
  delete: async (id) => {
    return apiRequest(`/agents/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Chat with agent
   */
  chat: async (agentId, message, conversationId = null) => {
    return apiRequest(`/agents/${agentId}/chat`, {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  },
};

/**
 * User API
 */
export const userAPI = {
  /**
   * Get current user profile
   */
  getProfile: async () => {
    return apiRequest('/users/me');
  },

  /**
   * Update user profile
   */
  updateProfile: async (userData) => {
    return apiRequest('/users/me', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Update API keys
   */
  updateKeys: async (keys) => {
    return apiRequest('/users/me/keys', {
      method: 'PUT',
      body: JSON.stringify(keys),
    });
  },
};

export default {
  authAPI,
  swaggerAPI,
  agentAPI,
  userAPI,
};
