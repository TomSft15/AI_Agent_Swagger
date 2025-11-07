/**
 * Chat Page
 *
 * Chat interface to interact with AI agents
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { ArrowLeft, Send, Bot, User } from 'lucide-react';
import { agentAPI } from '../services/api';
import './Chat.css';

const Chat = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { agentId: paramAgentId } = useParams();
  const messagesEndRef = useRef(null);

  const [selectedAgent, setSelectedAgent] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState(null);

  // Get agent ID from params or location state
  const agentId = paramAgentId || location.state?.agentId;

  useEffect(() => {
    if (agentId) {
      loadAgent(agentId);
    } else {
      setError('No agent selected');
    }
  }, [agentId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadAgent = async (id) => {
    try {
      setLoading(true);
      setError('');
      const agent = await agentAPI.getById(id);
      setSelectedAgent(agent);

      // Add welcome message (use custom message if available, otherwise default)
      const welcomeMessage = agent.welcome_message ||
        `Hello! I'm ${agent.name}. ${agent.description || 'How can I help you today?'}`;

      setMessages([
        {
          role: 'assistant',
          content: welcomeMessage,
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      console.error('[Chat] Load agent error:', err);
      setError('Failed to load agent: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim() || loading) {
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      // Call the chat API with the current conversation ID
      const response = await agentAPI.chat(
        agentId,
        currentMessage,
        conversationId
      );

      // Store the conversation ID for the session
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        conversation_id: response.conversation_id,
        function_calls: response.function_calls,
        api_calls: response.api_calls
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Log function calls if any were made
      if (response.function_calls && response.function_calls.length > 0) {
        console.log('[Chat] Function calls made:', response.function_calls);
      }
      if (response.api_calls && response.api_calls.length > 0) {
        console.log('[Chat] API calls made:', response.api_calls);
      }
    } catch (err) {
      console.error('[Chat] Send message error:', err);
      setError('Failed to send message: ' + err.message);

      // Remove the user message if the API call failed
      setMessages(prev => prev.slice(0, -1));
      // Restore the input
      setInputMessage(currentMessage);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!agentId) {
    return (
      <div className="chat-container">
        <div className="chat-header">
          <button onClick={() => navigate('/')} className="back-button">
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
        </div>
        <div className="chat-error">
          <p>No agent selected. Please select an agent from the dashboard.</p>
          <button onClick={() => navigate('/')} className="primary-button">
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button onClick={() => navigate('/')} className="back-button">
          <ArrowLeft size={20} />
          Back
        </button>
        <div className="chat-header-info">
          {selectedAgent && (
            <>
              <Bot size={24} />
              <div className="agent-info">
                <h2>{selectedAgent.name}</h2>
                <span className="agent-model">
                  {selectedAgent.llm_provider}/{selectedAgent.llm_model}
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="chat-error-banner">
          <div className="error-content">
            {error}
            {error.includes('URL') && error.includes('protocol') && (
              <div className="error-help">
                💡 Tip: Go to the Swagger document view to configure the base URL with http:// or https://
              </div>
            )}
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role === 'user' ? 'message-user' : 'message-assistant'}`}
          >
            <div className="message-icon">
              {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message message-assistant">
            <div className="message-icon">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="message-text typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={loading || !selectedAgent}
        />
        <button
          type="submit"
          className="send-button"
          disabled={loading || !inputMessage.trim() || !selectedAgent}
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default Chat;
