# Frontend Setup Guide

## Installation

1. **Install dependencies**

   First, you need to install the required npm packages listed in `dependencies.txt`:

   ```bash
   npm install axios react-router-dom
   ```

   Or install all at once:
   ```bash
   npm install
   ```

2. **Configure environment variables**

   Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

   Update the backend API URL if needed (default is `http://localhost:8000/api/v1`).

## Running the Application

1. **Start the development server**

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173` (or another port if 5173 is busy).

2. **Make sure the backend is running**

   The frontend needs the backend API to be running. Start the backend server:
   ```bash
   cd ../Backend
   docker-compose up
   ```

## Project Structure

```
Frontend/
├── src/
│   ├── contexts/
│   │   └── AuthContext.jsx       # Authentication state management
│   ├── pages/
│   │   ├── Login.jsx              # Login/Register page
│   │   ├── Login.css              # Login page styles
│   │   ├── Dashboard.jsx          # Main dashboard after login
│   │   └── Dashboard.css          # Dashboard styles
│   ├── services/
│   │   └── api.js                 # API service (HTTP requests)
│   ├── App.jsx                    # Main app component with routing
│   ├── App.css                    # Global styles
│   └── main.jsx                   # Entry point
├── .env                           # Environment variables
├── .env.example                   # Example environment variables
├── dependencies.txt               # List of required npm packages
└── package.json                   # Project configuration
```

## Features

### Authentication
- **Login**: Existing users can log in with email and password
- **Register**: New users can create an account
- **Auto-login**: After registration, users are automatically logged in
- **Token storage**: JWT tokens are stored in localStorage
- **Protected routes**: Dashboard is only accessible when authenticated

### API Integration
The application integrates with the backend API for:
- User authentication (login, register)
- User profile management
- Swagger document management
- AI agent creation and management
- Chat with AI agents

### Pages

1. **Login Page** (`/`)
   - Toggle between Login and Register forms
   - Form validation
   - Error display
   - Modern gradient design

2. **Dashboard** (after login)
   - Welcome message with user info
   - Quick access cards for main features
   - Getting started guide
   - Logout button

## Environment Variables

- `VITE_API_URL`: Backend API base URL (default: `http://localhost:8000/api/v1`)

## Development Notes

- The app uses Vite for fast development and building
- React 19 with hooks for state management
- No UI library dependencies (pure CSS)
- Fetch API for HTTP requests (no axios dependency if you prefer native)

## Building for Production

```bash
npm run build
```

The production-ready files will be in the `dist/` directory.

## Troubleshooting

### CORS Issues
If you encounter CORS errors, make sure the backend has the correct CORS configuration in `Backend/app/core/config.py`:

```python
BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173"]
```

### API Connection Failed
- Verify the backend is running on `http://localhost:8000`
- Check the `.env` file has the correct `VITE_API_URL`
- Check the browser console for detailed error messages

### Login Not Working
- Make sure you have created a user account (use the Register tab)
- Check the backend logs for authentication errors
- Verify the API keys are configured in your user profile if needed
