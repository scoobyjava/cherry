// Dashboard functionality
document.addEventListener('DOMContentLoaded', () => {
    // Fetch tasks data
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            renderTasks(data.tasks);
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
            document.getElementById('task-container').innerHTML = '<p>Error loading tasks</p>';
        });

    // Fetch leaderboard data
    fetch('/api/leaderboard')
        .then(response => response.json())
        .then(data => {
            renderLeaderboard(data.agents);
        })
        .catch(error => {
            console.error('Error fetching leaderboard:', error);
            document.getElementById('leaderboard-container').innerHTML = '<p>Error loading agent data</p>';
        });

    // Fetch agent network data
    fetch('/api/agent-network')
        .then(response => response.json())
        .then(data => {
            renderAgentNetwork(data);
        })
        .catch(error => {
            console.error('Error fetching agent network:', error);
            document.getElementById('network-visualization').innerHTML = '<p>Error loading network visualization</p>';
        });
});

// Render tasks list
function renderTasks(tasks) {
    const container = document.getElementById('task-container');
    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p>No active tasks</p>';
        return;
    }

    const taskList = document.createElement('ul');
    taskList.className = 'tasks';
    
    tasks.forEach(task => {
        const taskItem = document.createElement('li');
        taskItem.className = `task-item ${task.status}`;
        
        const taskName = document.createElement('h3');
        taskName.textContent = task.name;
        
        const taskDetails = document.createElement('div');
        taskDetails.className = 'task-details';
        taskDetails.innerHTML = `
            <p><strong>Status:</strong> ${task.status}</p>
            <p><strong>Assigned to:</strong> ${task.assigned_to}</p>
            <p><strong>Priority:</strong> ${task.priority}</p>
            <div class="progress-bar">
                <div class="progress" style="width: ${task.completion}%"></div>
            </div>
            <p>${task.completion}% complete</p>
        `;
        
        taskItem.appendChild(taskName);
        taskItem.appendChild(taskDetails);
        taskList.appendChild(taskItem);
    });
    
    container.innerHTML = '';
    container.appendChild(taskList);
}

// Render leaderboard
function renderLeaderboard(agents) {
    const container = document.getElementById('leaderboard-container');
    if (!agents || agents.length === 0) {
        container.innerHTML = '<p>No agent data available</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'leaderboard-table';
    
    // Create table header
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Agent</th>
            <th>Success Rate</th>
            <th>Efficiency</th>
            <th>Tasks</th>
        </tr>
    `;
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    agents.forEach(agent => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${agent.name}</td>
            <td>${agent.success_rate}%</td>
            <td>${agent.efficiency_score}</td>
            <td>${agent.tasks_handled}</td>
        `;
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    
    container.innerHTML = '';
    container.appendChild(table);
}


// Render agent network visualization using D3.js
function//-
function renderAgentNetwork(data) {//+
    const container = document.getElementById('network-visualization');//+
    container.innerHTML = '';//+
//+
    if (!data || !data.nodes || !data.links || data.nodes.length === 0) {//+
        container.innerHTML = '<p>No network data available</p>';//+
        return;//+
    }//+
//+
    // Set up the dimensions for the visualization//+
    const width = container.clientWidth;//+
    const height = 400;//+
//+
    // Create SVG element//+
    const svg = d3.select(container)//+
        .append('svg')//+
        .attr('width', width)//+
        .attr('height', height)//+
        .attr('viewBox', [0, 0, width, height])//+
        .attr('class', 'network-graph');//+
//+
    // Create a force simulation//+
    const simulation = d3.forceSimulation(data.nodes)//+
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))//+
        .force('charge', d3.forceManyBody().strength(-300))//+
        .force('center', d3.forceCenter(width / 2, height / 2))//+
        .force('collision', d3.forceCollide().radius(40));//+
//+
    // Create links//+
    const link = svg.append('g')//+
        .attr('class', 'links')//+
        .selectAll('line')//+
        .data(data.links)//+
        .enter()//+
        .append('line')//+
        .attr('stroke-width', d => Math.sqrt(d.value))//+
        .attr('stroke', '#999')//+
        .attr('stroke-opacity', 0.6);//+
//+
    // Create nodes//+
    const node = svg.append('g')//+
        .attr('class', 'nodes')//+
        .selectAll('g')//+
        .data(data.nodes)//+
        .enter()//+
        .append('g')//+
        .call(d3.drag()//+
            .on('start', dragstarted)//+
            .on('drag', dragged)//+
            .on('end', dragended));//+
//+
    // Add circles to nodes//+
    node.append('circle')//+
        .attr('r', 20)//+
        .attr('fill', d => getAgentColor(d.type))//+
        .attr('stroke', '#fff')//+
        .attr('stroke-width', 1.5);//+
//+
    // Add text labels to nodes//+
    node.append('text')//+
        .text(d => d.id)//+
        .attr('text-anchor', 'middle')//+
        .attr('dy', '.35em')//+
        .attr('fill', '#fff')//+
        .attr('font-size', '10px');//+
//+
    // Add titles for tooltips//+
    node.append('title')//+
        .text(d => `${d.id}: ${d.description || 'Agent'}`);//+
//+
    // Update positions on each tick of the simulation//+
    simulation.on('tick', () => {//+
        link//+
            .attr('x1', d => d.source.x)//+
            .attr('y1', d => d.source.y)//+
            .attr('x2', d => d.target.x)//+
            .attr('y2', d => d.target.y);//+
//+
        node//+
            .attr('transform', d => `translate(${d.x},${d.y})`);//+
    });//+
//+
    // Drag functions//+
    function dragstarted(event, d) {//+
        if (!event.active) simulation.alphaTarget(0.3).restart();//+
        d.fx = d.x;//+
        d.fy = d.y;//+
    }//+
//+
    function dragged(event, d) {//+
        d.fx = event.x;//+
        d.fy = event.y;//+
    }//+
//+
    function dragended(event, d) {//+
        if (!event.active) simulation.alphaTarget(0);//+
        d.fx = null;//+
        d.fy = null;//+
    }//+
//+
    // Helper function to get color based on agent type//+
    function getAgentColor(type) {//+
        const colorMap = {//+
            'code_agent': '#e91e63',      // pink//+
            'uiux_agent': '#2196f3',      // blue//+
            'documentation_agent': '#4caf50', // green//+
            'creative_agent': '#ff9800',  // orange//+
            'default': '#9c27b0'          // purple//+
        };//+
//+
        return colorMap[type] || colorMap.default;//+
    }//+
}//+
>>>>>>> Tabnine >>>>>>>// {"source":"chat"}