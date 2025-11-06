/**
 * API Service
 *
 * Handles all HTTP requests to the backend API
 */

// Base URL for the backend API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Flag to prevent multiple simultaneous refresh attempts
let isRefreshing = false;
let refreshPromise = null;

/**
 * Refresh the access token using the refresh token
 */
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');

  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    console.log('[API] Refreshing access token...');

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();

    // Update tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    console.log('[API] Access token refreshed successfully');
    return data.access_token;

  } catch (error) {
    console.error('[API] Token refresh failed:', error);
    // Clear tokens on refresh failure
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    throw error;
  }
}

/**
 * Make an HTTP request to the API
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  // Get token from localStorage
  let token = localStorage.getItem('access_token');

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
      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && endpoint !== '/auth/refresh' && endpoint !== '/auth/login') {
        console.log('[API] 401 Unauthorized - attempting token refresh');

        // Prevent multiple simultaneous refresh attempts
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = refreshAccessToken()
            .finally(() => {
              isRefreshing = false;
              refreshPromise = null;
            });
        }

        try {
          // Wait for token refresh
          const newToken = await refreshPromise;

          // Retry the original request with new token
          console.log('[API] Retrying request with new token');
          headers['Authorization'] = `Bearer ${newToken}`;

          const retryResponse = await fetch(url, {
            ...options,
            headers,
          });

          const retryData = await retryResponse.json().catch(() => ({}));

          if (!retryResponse.ok) {
            console.error(`[API] Retry failed ${retryResponse.status}:`, retryData);
            throw new Error(retryData.detail || `HTTP ${retryResponse.status}: ${retryResponse.statusText}`);
          }

          console.log(`[API] Retry success:`, retryData);
          return retryData;

        } catch (refreshError) {
          console.error('[API] Token refresh failed, redirecting to login');
          // Token refresh failed, user needs to login again
          throw new Error('Session expired. Please login again.');
        }
      }

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
   * Refresh access token
   */
  refresh: async () => {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiRequest('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    // Store new tokens
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
    }
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }

    return response;
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

  /**
   * Get endpoint customizations for a swagger document
   */
  getCustomizations: async (id) => {
    return apiRequest(`/swagger/${id}/customizations`);
  },

  /**
   * Update endpoint custom description and/or enabled status
   */
  updateCustomization: async (swaggerId, operationId, customDescription, isEnabled) => {
    const body = {};
    if (customDescription !== undefined) {
      body.custom_description = customDescription;
    }
    if (isEnabled !== undefined) {
      body.is_enabled = isEnabled;
    }

    return apiRequest(`/swagger/${swaggerId}/customizations/${operationId}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },

  /**
   * Delete endpoint customization (reset to default)
   */
  deleteCustomization: async (swaggerId, operationId) => {
    return apiRequest(`/swagger/${swaggerId}/customizations/${operationId}`, {
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
    return apiRequest('/agents/');
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

  /**
   * Regenerate agent from swagger
   */
  regenerate: async (agentId) => {
    return apiRequest(`/agents/${agentId}/regenerate`, {
      method: 'POST',
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
   * Get API keys (masked)
   */
  getKeys: async () => {
    return apiRequest('/users/me/keys');
  },

  /**
   * Update API keys
   */
  updateKeys: async (keys) => {
    return apiRequest('/users/me/llm-keys', {
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
