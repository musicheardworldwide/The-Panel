/**
 * The Panel - Client-side JavaScript
 * 
 * This script handles the interaction with the backend API and UI functionality.
 */

// Configuration
const API_BASE_URL = window.location.origin;
const ENDPOINTS = {
    chat: `${API_BASE_URL}/chat`,
    health: `${API_BASE_URL}/health`,
    config: `${API_BASE_URL}/config`,
};

// DOM Elements
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');
const processingIndicator = document.getElementById('processing-indicator');
const statusIndicator = document.getElementById('status-indicator');
const serverStatus = document.getElementById('server-status');
const clearHistoryButton = document.getElementById('clear-history');
const modelName = document.getElementById('model-name');
const modelOffline = document.getElementById('model-offline');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Check server health
    checkHealth();
    
    // Set up event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    clearHistoryButton.addEventListener('click', clearChatHistory);
    
    // Load chat history from localStorage
    loadChatHistory();
});

/**
 * Check the server health and update the UI
 */
function checkHealth() {
    fetch(ENDPOINTS.health)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update status indicators
            statusIndicator.classList.remove('bg-warning');
            statusIndicator.classList.add('bg-online');
            serverStatus.textContent = 'Server Online';
            
            // Update model info
            modelName.textContent = data.model || 'Unknown';
            modelOffline.textContent = data.offline ? 'Yes' : 'No';
        })
        .catch(error => {
            console.error('Health check error:', error);
            statusIndicator.classList.remove('bg-warning');
            statusIndicator.classList.add('bg-offline');
            serverStatus.textContent = 'Server Offline';
            
            // Show error in chat
            addSystemMessage('Server is currently offline. Please try again later.');
        });
}

/**
 * Send a message to the server
 */
function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input during processing
    setProcessingState(true);
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    userInput.value = '';
    
    // Send request to server
    fetch(ENDPOINTS.chat, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: message }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Add response to chat
            addBotMessage(data.response);
            
            // Save chat history
            saveChatHistory();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            addSystemMessage('Error: Could not get a response from the server. Please try again.');
        })
        .finally(() => {
            setProcessingState(false);
        });
}

/**
 * Add a user message to the chat
 */
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.textContent = text;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // Save to chat history
    saveChatHistory();
}

/**
 * Add a bot message to the chat with Markdown support
 */
function addBotMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    // Parse markdown
    const parsedContent = marked.parse(text);
    messageDiv.innerHTML = parsedContent;
    
    // Apply syntax highlighting
    messageDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add a system message to the chat
 */
function addSystemMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system-message';
    messageDiv.textContent = text;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Scroll to the bottom of the chat container
 */
function scrollToBottom() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Set the processing state of the UI
 */
function setProcessingState(isProcessing) {
    userInput.disabled = isProcessing;
    sendButton.disabled = isProcessing;
    
    if (isProcessing) {
        processingIndicator.classList.remove('d-none');
    } else {
        processingIndicator.classList.add('d-none');
    }
}

/**
 * Save chat history to localStorage
 */
function saveChatHistory() {
    const chatHistory = chatMessages.innerHTML;
    localStorage.setItem('chatHistory', chatHistory);
}

/**
 * Load chat history from localStorage
 */
function loadChatHistory() {
    const chatHistory = localStorage.getItem('chatHistory');
    
    if (chatHistory) {
        chatMessages.innerHTML = chatHistory;
        scrollToBottom();
    }
}

/**
 * Clear chat history
 */
function clearChatHistory() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatMessages.innerHTML = '';
        localStorage.removeItem('chatHistory');
        
        // Add welcome message again
        addSystemMessage('Chat history cleared. Ask anything to get started again.');
    }
}