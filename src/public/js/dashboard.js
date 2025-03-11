// Initialize socket connection
const socket = io();

// DOM elements
const systemLoad = document.getElementById('system-load');
const activeAgents = document.getElementById('active-agents');
const memoryUsage = document.getElementById('memory-usage');
const recentActivity = document.getElementById('recent-activity');
const quickAgentList = document.getElementById('quick-agent-list');
const agentGrid = document.getElementById('agent-grid');

// Navigation
document.querySelectorAll('nav ul li a').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = link.getAttribute('href').substring(1);
    
    // Hide all sections
    document.querySelectorAll('section').forEach(section => {
      section.classList.remove('active');
    });
    
    // Show target section
    document.getElementById(targetId).classList.add('active');
    

    // Update active nav item
    document.querySelectorAll('nav ul li').forEach(item => {
      item.classList.remove('active');
    });
    link.parentElement.classList.add('active');
  });
});

// Fetch agents data
async function fetchAgents() {
  try {
    const response = await fetch('/api/cherry/agents');
    const data = await response.json();
    
    if (data.agents) {
      updateAgentDisplay(data.agents);
    }
  } catch (error) {
    console.error('Error fetching agents:', error);
  }
}

// Update agent display
function updateAgentDisplay(agents) {
  // Update active agents count
  const activeCount = Object.values(agents).filter(agent => agent.status === 'active').length;
  activeAgents.textContent = `${activeCount}/${Object.keys(agents).length}`;
  
  // Update quick agent list
  quickAgentList.innerHTML = '';
  Object.entries(agents).forEach(([id, agent]) => {
    const agentEl = document.createElement('div');
    agentEl.className = `agent-item ${agent.status}`;
    agentEl.innerHTML = `
      <span class="agent-name">${agent.name}</span>
      <span class="agent-status">${agent.status}</span>
    `;
    quickAgentList.appendChild(agentEl);
  });
  
  // Update agent grid
  if (agentGrid) {
    agentGrid.innerHTML = '';
    Object.entries(agents).forEach(([id, agent]) => {
      const agentCard = document.createElement('div');
      agentCard.className = `agent-card ${agent.status}`;
      agentCard.innerHTML = `
        <div class="agent-header">
          <h3>${agent.name}</h3>
          <span class="status-badge ${agent.status}">${agent.status}</span>
        </div>
        <div class="agent-role">${agent.role}</div>
        <div class="agent-actions">
          <button class="btn btn-primary" onclick="interactWithAgent('${id}')">Interact</button>
          <button class="btn btn-secondary" onclick="viewAgentDetails('${id}')">Details</button>
        </div>
      `;
      agentGrid.appendChild(agentCard);
    });
  }
}

// Fetch system metrics
async function fetchSystemMetrics() {
  try {
    // This would be a real API endpoint in production
    const metrics = {
      systemLoad: 78,
      memoryUsage: 3.2,
      recentActivities: [
        { time: '10:45 AM', description: 'Code Analyzer completed code review', agent: 'code-analyzer' },
        { time: '10:30 AM', description: 'Memory Curator updated knowledge base', agent: 'memory-curator' },
        { time: '10:15 AM', description: 'System optimization completed', agent: 'cherry' }
      ]
    };
    
    updateMetricsDisplay(metrics);
  } catch (error) {
    console.error('Error fetching metrics:', error);
  }
}

// Update metrics display
function updateMetricsDisplay(metrics) {
  systemLoad.textContent = `${metrics.systemLoad}%`;
  memoryUsage.textContent = `${metrics.memoryUsage} GB`;
  
  // Update activity feed
  recentActivity.innerHTML = '';
  metrics.recentActivities.forEach(activity => {
    const activityEl = document.createElement('div');
    activityEl.className = 'activity-item';
    activityEl.innerHTML = `
      <span class="activity-time">${activity.time}</span>
      <span class="activity-description">${activity.description}</span>
      <span class="activity-agent">${activity.agent}</span>
    `;
    recentActivity.appendChild(activityEl);
  });
}

// Interact with an agent
function interactWithAgent(agentId) {
  console.log(`Interacting with agent: ${agentId}`);
  // This would open a chat interface with the agent
}

// View agent details
function viewAgentDetails(agentId) {
  console.log(`Viewing details for agent: ${agentId}`);
  // This would show detailed agent information
}

// Socket events
socket.on('connect', () => {
  console.log('Connected to Cherry server');
});

socket.on('metrics-update', (data) => {
  updateMetricsDisplay(data);
});

socket.on('agents-update', (data) => {
  updateAgentDisplay(data.agents);
});

// Initialize dashboard
fetchAgents();
fetchSystemMetrics();

// Refresh data periodically
setInterval(fetchAgents, 30000);
setInterval(fetchSystemMetrics, 10000);
