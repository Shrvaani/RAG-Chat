// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let currentConversationId = null;
let conversations = [];

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const newChatBtn = document.getElementById('newChatBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const sendBtn = document.getElementById('sendBtn');
const queryInput = document.getElementById('queryInput');
const messagesContainer = document.getElementById('messagesContainer');
const conversationList = document.getElementById('conversationList');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const loadingOverlay = document.getElementById('loadingOverlay');
const chatTitle = document.getElementById('chatTitle');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    await checkSystemHealth();
    await loadConversations();
    autoResizeTextarea();
}

function setupEventListeners() {
    // Upload events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    uploadBtn.addEventListener('click', () => fileInput.click());

    // Chat events
    newChatBtn.addEventListener('click', createNewConversation);
    clearChatBtn.addEventListener('click', clearCurrentChat);
    sendBtn.addEventListener('click', sendQuery);
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    });
    queryInput.addEventListener('input', autoResizeTextarea);
}

// System Health Check
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health/`);
        const data = await response.json();

        if (data.status === 'healthy') {
            statusDot.classList.add('healthy');
            statusText.textContent = 'System Online';
        } else {
            statusText.textContent = 'System Degraded';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusText.textContent = 'System Offline';
    }
}

// File Upload Handling
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    uploadFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    uploadFiles(files);
}

async function uploadFiles(files) {
    if (files.length === 0) return;

    showLoading(true);

    for (const file of files) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/documents/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                showNotification(`✅ ${file.name} uploaded successfully! (${data.chunks_created} chunks created)`, 'success');
            } else {
                showNotification(`❌ Failed to upload ${file.name}`, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showNotification(`❌ Error uploading ${file.name}`, 'error');
        }
    }

    showLoading(false);
    fileInput.value = '';
}

// Conversation Management
async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations/`);
        const data = await response.json();
        conversations = data.conversations;
        renderConversations();
    } catch (error) {
        console.error('Failed to load conversations:', error);
    }
}

function renderConversations() {
    conversationList.innerHTML = '';

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conv.conversation_id === currentConversationId) {
            item.classList.add('active');
        }

        item.innerHTML = `
            <div style="font-weight: 600;">${conv.title}</div>
            <div style="font-size: 0.85rem; opacity: 0.7;">${conv.message_count} messages</div>
        `;

        item.addEventListener('click', () => loadConversation(conv.conversation_id));
        conversationList.appendChild(item);
    });
}

async function createNewConversation() {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: `Chat ${new Date().toLocaleString()}` })
        });

        const data = await response.json();
        currentConversationId = data.conversation_id;
        chatTitle.textContent = data.title;

        messagesContainer.innerHTML = '<div class="welcome-message"><h3>👋 New Chat Started!</h3><p>Ask your first question.</p></div>';

        await loadConversations();
    } catch (error) {
        console.error('Failed to create conversation:', error);
        showNotification('❌ Failed to create new chat', 'error');
    }
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);
        const data = await response.json();

        currentConversationId = conversationId;
        chatTitle.textContent = data.title;

        messagesContainer.innerHTML = '';
        data.messages.forEach(msg => {
            addMessage(msg.content, msg.role, msg.citations, msg.timestamp);
        });

        renderConversations();
    } catch (error) {
        console.error('Failed to load conversation:', error);
    }
}

function clearCurrentChat() {
    if (confirm('Clear current chat?')) {
        messagesContainer.innerHTML = '<div class="welcome-message"><h3>👋 Chat Cleared!</h3><p>Start a new conversation.</p></div>';
        currentConversationId = null;
        chatTitle.textContent = 'Welcome to RAG Q&A';
    }
}

// Query Handling
async function sendQuery() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Add user message
    addMessage(query, 'user');
    queryInput.value = '';
    autoResizeTextarea();

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/query/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                conversation_id: currentConversationId,
                top_k: 5
            })
        });

        const data = await response.json();

        // Update conversation ID if new
        if (!currentConversationId) {
            currentConversationId = data.conversation_id;
            await loadConversations();
        }

        // Add assistant response
        addMessage(data.response, 'assistant', data.citations);

    } catch (error) {
        console.error('Query error:', error);
        addMessage('Sorry, I encountered an error processing your query. Please try again.', 'assistant');
    }

    showLoading(false);
}

// UI Helpers
function addMessage(content, role, citations = [], timestamp = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;

    let citationsHTML = '';
    if (citations && citations.length > 0) {
        citationsHTML = `
            <div class="citations">
                <h4>📚 Sources:</h4>
                ${citations.map((c, i) => `
                    <div class="citation">
                        [${c.id}] ${c.filename || c.title}
                        ${c.page ? ` (Page ${c.page})` : ''}
                        ${c.url ? `<br><a href="${c.url}" target="_blank">${c.url}</a>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    const time = timestamp || new Date().toLocaleTimeString();

    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${content.replace(/\n/g, '<br>')}
            ${citationsHTML}
            <div class="message-time">${time}</div>
        </div>
    `;

    // Remove welcome message if exists
    const welcome = messagesContainer.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showLoading(show) {
    loadingOverlay.classList.toggle('active', show);
}

function showNotification(message, type = 'info') {
    // Simple notification (could be enhanced with a toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}

function autoResizeTextarea() {
    queryInput.style.height = 'auto';
    queryInput.style.height = Math.min(queryInput.scrollHeight, 150) + 'px';
}
