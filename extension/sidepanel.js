document.addEventListener('DOMContentLoaded', () => {
    new StockResearchAssistant();
});

class StockResearchAssistant {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.querySelector('.typing-indicator');
        this.statusIndicator = document.querySelector('.status');
        this.backendUrl = 'http://localhost:5000';
        this.agentReadyAnnounced = false;
        this.offlineAnnounced = false;
        
        // Set the initial message
        this.chatContainer.innerHTML = '';
        this.addMessage("👋 Hello! I'm Cortex D Agent.<br>Please wait while the server is initializing...", 'assistant');
        
        this.setupEventListeners();
        this.setupSuggestions();
        this.setupAutoResize();
        this.checkServerStatus();
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.handleUserInput());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleUserInput();
            }
        });
    }

    setupSuggestions() {
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.userInput.value = btn.textContent.replace(/['"]/g, '');
                this.handleUserInput();
            });
        });
    }

    setupAutoResize() {
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = (this.userInput.scrollHeight) + 'px';
        });
    }

    async checkServerStatus() {
        try {
            const response = await fetch(`${this.backendUrl}/status`);
            if (!response.ok) {
                this.setInitializing();
                return;
            }
            const data = await response.json();
            if (data.status === 'ready') {
                this.setOnline();
            } else {
                this.setInitializing();
            }
        } catch (error) {
            this.setOffline();
        }
    }

    setInitializing() {
        this.statusIndicator.textContent = 'Initializing...';
        this.statusIndicator.className = 'status initializing';
        this.disableInput();
        this.offlineAnnounced = false;
        setTimeout(() => this.checkServerStatus(), 5000);
    }

    setOnline() {
        this.statusIndicator.textContent = 'Online';
        this.statusIndicator.className = 'status online';
        this.enableInput();
        this.offlineAnnounced = false;
        if (!this.agentReadyAnnounced) {
            this.chatContainer.innerHTML = '';
            this.addMessage("Agent is ready! Please type your query.", 'assistant');
            this.agentReadyAnnounced = true;
        }
    }

    setOffline() {
        this.statusIndicator.textContent = 'Offline';
        this.statusIndicator.className = 'status offline';
        this.disableInput();
        if (!this.offlineAnnounced) {
            this.addMessage('Unable to connect to the server. Please try again later.', 'assistant');
            this.offlineAnnounced = true;
        }
        setTimeout(() => this.checkServerStatus(), 10000);
    }

    enableInput() {
        this.userInput.disabled = false;
        this.sendButton.disabled = false;
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.disabled = false;
        });
    }

    disableInput() {
        this.userInput.disabled = true;
        this.sendButton.disabled = true;
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.disabled = true;
        });
    }

    async handleUserInput() {
        const message = this.userInput.value.trim();
        if (!message) return;

        this.disableInput();

        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.userInput.style.height = 'auto';

        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.backendUrl}/query?message=${encodeURIComponent(message)}`);
            if (!response.ok) {
                throw new Error('Server error');
            }
            const data = await response.json();
                    this.hideTypingIndicator();
                    
            if (data.type === 'final') {
                    this.addMessage(data.content, 'assistant');
                        setTimeout(() => {
                            this.addMessage("What else would you like to know?", 'assistant');
                        }, 500);
                        this.enableInput();
            } else if (data.error) {
                this.addMessage('Sorry, there was an error processing your request.', 'assistant');
                this.enableInput();
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, there was an error processing your request.', 'assistant');
            this.enableInput();
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (type === 'assistant') {
            // Allow HTML for assistant messages (so <br> and emoji work)
            messageContent.innerHTML = content;
        } else {
            // Escape HTML for user messages
            messageContent.innerHTML = `<p>${this.escapeHtml(content)}</p>`;
        }

        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = this.getTimestamp();

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);

        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    getTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString();
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
}