// Cherry Blossom Web Interface - Core Functionality
document.addEventListener('DOMContentLoaded', () => {
  // Initialize core components
  initializeTerminal();
  initializeConversationHistory();
  initializeSystemMonitor();
  initializeProjectManager();
  initializeMemorySearch();
  
  // Setup websocket connection for real-time updates
  const socket = new WebSocket(`ws://${window.location.host}/ws`);
  
  socket.onopen = () => {
    console.log('Connected to Cherry Blossom server');
    updateSystemStatus('Connected');
  };
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleServerMessage(data);
  };
});

// Terminal Component
function initializeTerminal() {
  const terminal = document.getElementById('terminal-input');
  const outputDisplay = document.getElementById('terminal-output');
  
  terminal.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const command = terminal.value.trim();
      
      if (command) {
        // Display user input in terminal
        appendToTerminal(`> ${command}`, 'user-command');
        
        // Send command to server
        sendCommand(command);
        
        // Clear input field
        terminal.value = '';
      }
    }
  });
  
  function appendToTerminal(text, className) {
    const entry = document.createElement('div');
    entry.textContent = text;
    entry.classList.add(className);
    outputDisplay.appendChild(entry);
    outputDisplay.scrollTop = outputDisplay.scrollHeight;
    
    // Also add to conversation history
    addToConversationHistory(text, className);
  }
  
  // Expose this function globally for other components
  window.appendToTerminal = appendToTerminal;
}

// Conversation History Component
function initializeConversationHistory() {
  const historyContainer = document.getElementById('conversation-history');
  
  window.addToConversationHistory = (text, type) => {
    const entry = document.createElement('div');
    entry.textContent = text;
    entry.classList.add('history-entry', type);
    
    // Add timestamp
    const timestamp = document.createElement('span');
    timestamp.textContent = new Date().toLocaleTimeString();
    timestamp.classList.add('timestamp');
    entry.appendChild(timestamp);
    
    historyContainer.appendChild(entry);
    
    // Store in localStorage for persistence
    const history = JSON.parse(localStorage.getItem('cherryConversationHistory') || '[]');
    history.push({
      text,
      type,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('cherryConversationHistory', JSON.stringify(history.slice(-100)));
  };
  
  // Load conversation history from localStorage
  function loadConversationHistory() {
    const history = JSON.parse(localStorage.getItem('cherryConversationHistory') || '[]');
    history.forEach(item => {
      const entry = document.createElement('div');
      entry.textContent = item.text;
      entry.classList.add('history-entry', item.type);
      
      const timestamp = document.createElement('span');
      timestamp.textContent = new Date(item.timestamp).toLocaleTimeString();
      timestamp.classList.add('timestamp');
      entry.appendChild(timestamp);
      
      historyContainer.appendChild(entry);
    });
  }
  
  loadConversationHistory();
}

// System Monitor Component
function initializeSystemMonitor() {
  const statusContainer = document.getElementById('system-status');
  const agentsContainer = document.getElementById('agent-statuses');
  
  window.updateSystemStatus = (status) => {
    const statusElement = document.getElementById('connection-status');
    statusElement.textContent = status;
    statusElement.className = status.toLowerCase().replace(' ', '-');
  };
  
  window.updateAgentStatus = (agent, status, metrics) => {
    let agentElement = document.getElementById(`agent-${agent}`);
    
    if (!agentElement) {
      agentElement = document.createElement('div');
      agentElement.id = `agent-${agent}`;
      agentElement.classList.add('agent-status-card');
      agentsContainer.appendChild(agentElement);
    }
    
    agentElement.innerHTML = `
      <h3>${agent}</h3>
      <div class="status-indicator ${status.toLowerCase()}"></div>
      <div class="agent-metrics">
        ${Object.entries(metrics).map(([key, value]) => 
          `<div class="metric"><span>${key}:</span> ${value}</div>`
        ).join('')}
      </div>
    `;
  };
  
  // Initialize with dummy data
  updateSystemStatus('Initializing');
  updateAgentStatus('CodeAnalyzer', 'active', {
    'Tasks': 0,
    'Performance': '0.85'
  });
  updateAgentStatus('MemoryCurator', 'standby', {
    'Tasks': 0,
    'Performance': '0.75'
  });
}

// Project Management Component
function initializeProjectManager() {
  const projectContainer = document.getElementById('project-container');
  
  window.addProject = (id, name, description, tasks, progress) => {
    const projectCard = document.createElement('div');
    projectCard.id = `project-${id}`;
    projectCard.classList.add('project-card');
    
    projectCard.innerHTML = `
      <h3>${name}</h3>
      <p>${description}</p>
      <div class="progress-bar">
        <div class="progress" style="width: ${progress}%"></div>
      </div>
      <div class="task-list">
        ${tasks.map(task => `
          <div class="task ${task.status}">
            <input type="checkbox" ${task.status === 'completed' ? 'checked' : ''}>
            <span>${task.name}</span>
          </div>
        `).join('')}
      </div>
    `;
    
    projectContainer.appendChild(projectCard);
  };
  
  // Add sample project
  addProject(1, 'Cherry Blossom Interface', 'Development of the web interface', [
    {name: 'Design UI Components', status: 'completed'},
    {name: 'Implement Terminal', status: 'in-progress'},
    {name: 'Connect to Backend API', status: 'pending'}
  ], 35);
}

// Memory Search Component
function initializeMemorySearch() {
  const searchInput = document.getElementById('memory-search');
  const resultsContainer = document.getElementById('search-results');
  
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const query = searchInput.value.trim();
      
      if (query) {
        // Show loading state
        resultsContainer.innerHTML = '<div class="loading">Searching Cherry\'s memory...</div>';
        
        // Send search query to server
        fetch('/api/memory/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query })
        })
        .then(response => response.json())
        .then(results => {
          displaySearchResults(results);
        })
        .catch(error => {
          resultsContainer.innerHTML = `<div class="error">Error searching memory: ${error.message}</div>`;
        });
      }
    }
  });
  
  function displaySearchResults(results) {
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
      resultsContainer.innerHTML = '<div class="no-results">No matching memories found</div>';
      return;
    }
    
    results.forEach(result => {
      const resultElement = document.createElement('div');
      resultElement.classList.add('memory-result');
      
      resultElement.innerHTML = `
        <h4>${result.title}</h4>
        <p>${result.snippet}</p>
        <div class="memory-meta">
          <span>Confidence: ${(result.score * 100).toFixed(1)}%</span>
          <span>Source: ${result.source}</span>
          <span>Date: ${new Date(result.timestamp).toLocaleDateString()}</span>
        </div>
      `;
      
      resultElement.addEventListener('click', () => {
        // Display full memory content
        showMemoryDetail(result);
      });
      
      resultsContainer.appendChild(resultElement);
    });
  }
  
  function showMemoryDetail(memory) {
    const modal = document.createElement('div');
    modal.classList.add('memory-modal');
    
    modal.innerHTML = `
      <div class="memory-modal-content">
        <span class="close-button">×</span>
        <h3>${memory.title}</h3>
        <div class="memory-content">${memory.content}</div>
        <div class="memory-actions">
          <button class="reference-button">Reference in Terminal</button>
          <button class="save-button">Save to Project</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.close-button').addEventListener('click', () => {
      modal.remove();
    });
    
    modal.querySelector('.reference-button').addEventListener('click', () => {
      window.appendToTerminal(`Memory Reference: ${memory.title}`, 'system-message');
      modal.remove();
    });
  }
}

// Utility for sending commands to server
function sendCommand(command) {
  fetch('/api/command', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ command })
  })
  .then(response => response.json())
  .then(data => {
    // Display response in terminal
    window.appendToTerminal(data.message, 'system-response');
    
    // Update any relevant components based on response
    if (data.agentUpdates) {
      data.agentUpdates.forEach(update => {
        updateAgentStatus(update.agent, update.status, update.metrics);
      });
    }
  })
  .catch(error => {
    window.appendToTerminal(`Error: ${error.message}`, 'error-message');
  });
}

// Handle incoming server messages (from websocket)
function handleServerMessage(data) {
  switch(data.type) {
    case 'terminal_response':
      window.appendToTerminal(data.message, 'system-response');
      break;
    case 'agent_update':
      updateAgentStatus(data.agent, data.status, data.metrics);
      break;
    case 'project_update':
      // Refresh project view
      document.getElementById(`project-${data.projectId}`)?.remove();
      addProject(data.projectId, data.name, data.description, data.tasks, data.progress);
      break;
    case 'memory_added':
      window.appendToTerminal(`Memory stored: ${data.title}`, 'system-message');
      break;
    default:
      console.log('Unknown message type:', data.type);
  }
}
