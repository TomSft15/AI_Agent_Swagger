# Frontend - AI Agent Swagger Platform

React-based frontend application for the AI Agent Swagger Platform. Provides a modern, intuitive interface for managing Swagger documents, creating AI agents, and customizing API functions.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Components](#components)
- [Pages](#pages)
- [State Management](#state-management)
- [Routing](#routing)
- [Development](#development)

## 🏗️ Architecture

### Project Structure

```
Frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable React components
│   │   ├── FunctionEditor.jsx
│   │   ├── FunctionEditor.css
│   │   └── ProtectedRoute.jsx
│   ├── pages/            # Page components
│   │   ├── Login.jsx
│   │   ├── Login.css
│   │   ├── Dashboard.jsx
│   │   ├── Dashboard.css
│   │   ├── AgentManager.jsx
│   │   ├── AgentManager.css
│   │   ├── AgentEdit.jsx
│   │   ├── AgentEdit.css
│   │   ├── SwaggerView.jsx
│   │   ├── SwaggerView.css
│   │   ├── ManageKeys.jsx
│   │   └── ManageKeys.css
│   ├── services/         # API service layer
│   │   └── api.js
│   ├── App.jsx           # Main application component
│   ├── App.css           # Global styles
│   └── main.jsx          # Application entry point
├── index.html
├── package.json
├── vite.config.js
└── README.md             # This file
```

### Technology Stack

- **React 18** - UI library
- **React Router v6** - Client-side routing
- **Vite** - Build tool and dev server
- **Lucide React** - Icon library
- **Fetch API** - HTTP client with auto-refresh

### Design Patterns

1. **Component-Based Architecture**
   - Reusable components with single responsibility
   - Props for data flow
   - Ref forwarding for parent-child communication

2. **Service Layer Pattern**
   - Centralized API calls in `services/api.js`
   - Automatic token refresh
   - Error handling and retry logic

3. **Protected Routes**
   - Authentication check on route level
   - Automatic redirect to login
   - Token validation

## 🚀 Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd Frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL
```

### Environment Variables

Create a `.env` file in the Frontend directory:

```bash
VITE_API_URL=http://localhost:5000/api/v1
```

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Access

- Development: http://localhost:8080
- Production build preview: http://localhost:4173

## 🧩 Components

### FunctionEditor

Advanced component for customizing Swagger endpoints.

**Location:** `src/components/FunctionEditor.jsx`

**Features:**
- Toggle endpoints on/off
- Edit custom descriptions
- Local state management (changes not saved until "Save & Regenerate")
- Visual feedback with badges (Custom, Disabled)
- Reset to default functionality

**Props:**
```javascript
<FunctionEditor
  ref={functionEditorRef}
  swaggerId={parseInt(swaggerId)}
  endpoints={endpoints}
  onHasChanges={setHasChanges}
/>
```

**Ref Methods:**
```javascript
functionEditorRef.current.saveAllChanges()  // Save all modifications
functionEditorRef.current.hasChanges()      // Check if there are unsaved changes
```

**State Management:**
- `savedCustomizations` - Customizations from database
- `localCustomizations` - Local modifications (not yet saved)
- `editingEndpoint` - Currently editing endpoint ID
- `editValue` - Current description being edited

**Key Functions:**
- `loadCustomizations()` - Fetch from API
- `toggleEnabledLocal(endpoint)` - Toggle enable/disable (local only)
- `saveDescriptionLocal(endpoint)` - Apply description change (local only)
- `resetDescriptionLocal(endpoint)` - Reset to default (local only)
- `saveAllChanges()` - Save all local changes to API

### ProtectedRoute

HOC for route protection with authentication.

**Location:** `src/components/ProtectedRoute.jsx`

**Usage:**
```javascript
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

**Logic:**
- Checks for `access_token` in localStorage
- Redirects to `/login` if not authenticated
- Preserves intended destination for post-login redirect

## 📄 Pages

### Login (`src/pages/Login.jsx`)

User authentication page.

**Features:**
- Email/username + password login
- Token storage (access + refresh)
- Error handling
- Redirect to intended page after login

**State:**
- `emailOrUsername` - Login identifier
- `password` - User password
- `error` - Error message
- `loading` - Loading state

### Dashboard (`src/pages/Dashboard.jsx`)

Main dashboard with navigation cards.

**Features:**
- Overview of agents count
- Navigation to main features
- User greeting
- Quick stats display

**Cards:**
- Create Agent
- Manage Keys
- View Documentation

### AgentManager (`src/pages/AgentManager.jsx`)

List and manage all agents.

**Features:**
- Agent list with search/filter
- Create new agent workflow
- Upload Swagger
- Agent configuration
- Quick actions (Edit, Delete)

**State:**
- `agents` - List of user agents
- `swaggerDocs` - Available Swagger documents
- `step` - Current step in creation wizard
- `showUpload` - Upload dialog visibility

**Steps:**
1. List existing agents
2. Create agent button → Show upload or select existing Swagger
3. Configure agent (name, description, LLM settings)
4. Create agent

### AgentEdit (`src/pages/AgentEdit.jsx`)

Edit agent configuration.

**Features:**
- Update agent settings
- LLM provider and model selection
- Temperature and max tokens control
- Activate/deactivate agent
- View agent information (Swagger, functions count)

**Form Fields:**
- `name` - Agent name
- `description` - Agent description
- `llm_provider` - LLM provider (OpenAI, Anthropic, Mistral, Ollama)
- `llm_model` - Model name
- `temperature` - 0-100 (creativity)
- `max_tokens` - Response length
- `is_active` - Active/inactive toggle

### SwaggerView (`src/pages/SwaggerView.jsx`)

View and customize Swagger document.

**Features:**
- Document information display
- Endpoint list
- Function customization with FunctionEditor
- Save & Regenerate Agents button
- Agent count display

**State:**
- `swagger` - Swagger document data
- `endpoints` - List of endpoints
- `agents` - Agents using this Swagger
- `hasChanges` - Unsaved changes flag
- `saving` - Save in progress

**Workflow:**
1. Display Swagger information
2. Show all endpoints with customization options
3. User modifies functions (local state)
4. Click "Save & Regenerate Agents"
5. Save customizations + Regenerate all agents
6. Show success message

### ManageKeys (`src/pages/ManageKeys.jsx`)

Manage LLM API keys.

**Features:**
- Add/update OpenAI API key
- Add/update Anthropic API key
- Show/hide key values
- Masked display of existing keys
- Secure storage (encrypted in backend)

**State:**
- `keys` - API keys (openai_api_key, anthropic_api_key)
- `showKeys` - Visibility toggle for each key
- `saving` - Save in progress

## 🔌 Services

### API Service (`src/services/api.js`)

Centralized API communication layer.

**Features:**
- JWT authentication with automatic refresh
- CORS handling
- Error handling
- Request/response interceptors

**Modules:**

#### `authAPI`
- `login(emailOrUsername, password)` - User login
- `register(userData)` - User registration
- `refresh()` - Refresh access token
- `logout()` - Clear tokens
- `getCurrentUser()` - Get current user info

#### `swaggerAPI`
- `getAll()` - List Swagger documents
- `upload(file, name, description, base_url)` - Upload Swagger file
- `getById(id)` - Get Swagger document
- `getEndpoints(id)` - Get endpoints
- `delete(id)` - Delete Swagger document
- `getCustomizations(id)` - Get endpoint customizations
- `updateCustomization(swaggerId, operationId, customDescription, isEnabled)` - Update customization
- `deleteCustomization(swaggerId, operationId)` - Delete customization

#### `agentAPI`
- `getAll()` - List agents
- `create(agentData)` - Create agent
- `getById(id)` - Get agent details
- `update(id, agentData)` - Update agent
- `delete(id)` - Delete agent
- `chat(agentId, message, conversationId)` - Chat with agent
- `regenerate(agentId)` - Regenerate agent from Swagger

#### `userAPI`
- `getProfile()` - Get user profile
- `updateProfile(userData)` - Update profile
- `getKeys()` - Get API keys (masked)
- `updateKeys(keys)` - Update API keys

**Auto-Refresh Logic:**
```javascript
1. Request fails with 401
2. Check if not login/refresh endpoint
3. Call refreshAccessToken()
4. Get new access token
5. Retry original request
6. If refresh fails → logout
```

## 🎨 Styling

### CSS Architecture

- **Component-scoped CSS** - Each component has its own CSS file
- **BEM-like naming** - Block Element Modifier pattern
- **Consistent color palette** - Purple gradient theme (#667eea to #764ba2)
- **Responsive design** - Mobile-first approach

### Common Classes

```css
/* Buttons */
.btn-primary       /* Primary action button (gradient) */
.btn-secondary     /* Secondary action button (gray) */
.btn-edit          /* Edit button (purple) */
.btn-save          /* Save button (green) */
.btn-cancel        /* Cancel button (gray) */
.btn-reset         /* Reset button (gray outline) */

/* Cards */
.info-card         /* Information display card */
.actions-card      /* Action buttons container */
.function-item     /* Function editor item */

/* Badges */
.method-badge      /* HTTP method badge (GET, POST, etc.) */
.custom-badge      /* Custom description indicator */
.disabled-badge    /* Disabled function indicator */

/* Alerts */
.alert-error       /* Error message */
.alert-success     /* Success message */

/* Layout */
.spinner           /* Loading spinner */
.toggle-switch     /* Toggle switch component */
```

### Color Palette

```css
/* Primary Colors */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--primary-purple: #667eea;
--primary-dark: #5568d3;

/* Neutral Colors */
--gray-50: #f7fafc;
--gray-100: #edf2f7;
--gray-200: #e2e8f0;
--gray-300: #cbd5e0;
--gray-400: #a0aec0;
--gray-500: #718096;
--gray-600: #4a5568;
--gray-700: #2d3748;
--gray-800: #1a202c;

/* Status Colors */
--success: #48bb78;
--error: #e53e3e;
--warning: #ed8936;
--info: #4299e1;
```

## 🛣️ Routing

### Routes Definition

```javascript
<Routes>
  <Route path="/login" element={<Login />} />

  <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

  <Route path="/agent-manager" element={<ProtectedRoute><AgentManager /></ProtectedRoute>} />

  <Route path="/agents/:agentId/edit" element={<ProtectedRoute><AgentEdit /></ProtectedRoute>} />

  <Route path="/swagger/:swaggerId" element={<ProtectedRoute><SwaggerView /></ProtectedRoute>} />

  <Route path="/manage-keys" element={<ProtectedRoute><ManageKeys /></ProtectedRoute>} />
</Routes>
```

### Navigation

```javascript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

// Navigate to route
navigate('/agent-manager');

// Navigate with state
navigate('/swagger/123', { state: { from: 'dashboard' } });

// Navigate back
navigate(-1);
```

## 🔄 State Management

### Local Component State

Using React `useState` and `useEffect` hooks:

```javascript
const [data, setData] = useState([]);
const [loading, setLoading] = useState(false);
const [error, setError] = useState('');

useEffect(() => {
  fetchData();
}, [dependencies]);
```

### Form State

```javascript
const [formData, setFormData] = useState({
  name: '',
  description: '',
  temperature: 70
});

const handleChange = (e) => {
  setFormData({
    ...formData,
    [e.target.name]: e.target.value
  });
};
```

### Authentication State

Stored in localStorage:
- `access_token` - JWT access token (30 min TTL)
- `refresh_token` - JWT refresh token (7 day TTL)

### Ref Communication

For parent-child method invocation:

```javascript
// Parent
const childRef = useRef();
childRef.current.someMethod();

// Child (with forwardRef)
const Child = forwardRef((props, ref) => {
  useImperativeHandle(ref, () => ({
    someMethod: () => { /* implementation */ }
  }));

  return <div>...</div>;
});
```

## 🧪 Development

### Hot Module Replacement (HMR)

Vite provides instant HMR for React components:
- Changes reflect immediately
- Component state is preserved
- No full page reload

### Development Tools

```bash
# Install dependencies
npm install

# Start dev server with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Debugging

#### React DevTools

Install browser extension for component inspection and state debugging.

#### Network Tab

Monitor API calls:
- Request/response inspection
- Token refresh flow
- Error responses

#### Console Logging

Strategic logging in key areas:
```javascript
console.log('[ComponentName] Description:', data);
```

### Best Practices

1. **Component Organization**
   - Keep components small and focused
   - Extract reusable logic to custom hooks
   - Use prop destructuring

2. **Performance**
   - Use `React.memo()` for expensive renders
   - Debounce search inputs
   - Lazy load routes

3. **Error Handling**
   - Try-catch in async functions
   - User-friendly error messages
   - Fallback UI for errors

4. **Accessibility**
   - Semantic HTML
   - ARIA labels where needed
   - Keyboard navigation support

## 🎯 Key Features Implementation

### Automatic Token Refresh

Implemented in `services/api.js`:

```javascript
// On 401 error
if (response.status === 401) {
  // Refresh token
  await refreshAccessToken();

  // Retry request
  return apiRequest(endpoint, options);
}
```

### Function Customization Workflow

1. User views Swagger document
2. FunctionEditor loads customizations
3. User toggles functions / edits descriptions
4. Changes stored in local state (not saved)
5. Visual indicator shows unsaved changes
6. Click "Save & Regenerate" button
7. All customizations saved to backend
8. All agents using this Swagger regenerated
9. Success message displayed

### Protected Routes

All routes except `/login` require authentication:

```javascript
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" />;
  }

  return children;
};
```

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile */
@media (max-width: 768px) {
  /* Mobile styles */
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  /* Tablet styles */
}

/* Desktop */
@media (min-width: 1025px) {
  /* Desktop styles */
}
```

### Mobile-First Approach

- Default styles for mobile
- Progressive enhancement for larger screens
- Flexible layouts with flexbox/grid
- Touch-friendly button sizes

## 🔐 Security Considerations

1. **Token Storage**
   - Tokens in localStorage (accessible to XSS)
   - Consider httpOnly cookies for production
   - Implement CSP headers

2. **Input Validation**
   - Client-side validation for UX
   - Always validate on backend
   - Sanitize user inputs

3. **HTTPS Only**
   - Use HTTPS in production
   - Secure cookie flags
   - HSTS headers

## 📝 License

MIT License

---

**Development Server**: http://localhost:8080
**API Backend**: http://localhost:5000/api/v1
