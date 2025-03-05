import os
import logging
import asyncio
import json
import datetime
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx

from cherry.agents.message_bus import message_bus

logger = logging.getLogger(__name__)

class AgentSystemEvaluator:
    """
    Evaluates the performance of Cherry's multi-agent system by analyzing communication
    patterns, task execution metrics, and suggesting improvements.
    """
    
    def __init__(self):
        self.communication_log = []
        self.agent_metrics = defaultdict(lambda: {
            "tasks_received": 0,
            "tasks_completed": 0,
            "avg_response_time": 0,
            "failures": 0,
            "successful_collaborations": 0
        })
        self.workflow_bottlenecks = []
        self.improvement_suggestions = []
        
        # Task type distributions per agent
        self.agent_task_distribution = defaultdict(lambda: defaultdict(int))
        
        # Agent communication graph
        self.communication_graph = nx.DiGraph()
    
    async def log_communication(self, message: Dict[str, Any]) -> None:
        """Log inter-agent communication for analysis"""
        if not message or "sender" not in message or "recipient" not in message:
            return
            
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "sender": message["sender"],
            "recipient": message["recipient"],
            "message_type": message.get("type", "unknown"),
            "message_size": len(str(message.get("payload", ""))),
            "success": message.get("status", "") == "delivered"
        }
        
        self.communication_log.append(log_entry)
        
        # Update agent metrics
        if log_entry["success"]:
            self.agent_metrics[message["recipient"]]["tasks_received"] += 1
            
            # Update communication graph
            if not self.communication_graph.has_node(message["sender"]):
                self.communication_graph.add_node(message["sender"])
            if not self.communication_graph.has_node(message["recipient"]):
                self.communication_graph.add_node(message["recipient"])
            
            # Add or update edge weight (communication frequency)
            if self.communication_graph.has_edge(message["sender"], message["recipient"]):
                self.communication_graph[message["sender"]][message["recipient"]]["weight"] += 1
            else:
                self.communication_graph.add_edge(message["sender"], message["recipient"], weight=1)
    
    async def log_task_completion(self, agent_name: str, task_data: Dict[str, Any], 
                                 execution_time: float, success: bool) -> None:
        """Log task completion metrics"""
        self.agent_metrics[agent_name]["tasks_completed"] += 1 if success else 0
        self.agent_metrics[agent_name]["failures"] += 0 if success else 1
        
        # Update response time moving average
        prev_avg = self.agent_metrics[agent_name]["avg_response_time"]
        task_count = self.agent_metrics[agent_name]["tasks_completed"]
        if task_count > 1:
            self.agent_metrics[agent_name]["avg_response_time"] = \
                prev_avg + (execution_time - prev_avg) / task_count
        else:
            self.agent_metrics[agent_name]["avg_response_time"] = execution_time
            
        # Track task type distribution
        task_type = task_data.get("task_type", "unknown")
        self.agent_task_distribution[agent_name][task_type] += 1
    
    async def log_collaboration(self, initiator: str, collaborators: List[str], success: bool) -> None:
        """Log collaborative task execution"""
        if success:
            self.agent_metrics[initiator]["successful_collaborations"] += 1
            for agent in collaborators:
                self.agent_metrics[agent]["successful_collaborations"] += 1
    
    async def run_system_evaluation(self) -> Dict[str, Any]:
        """
        Perform a comprehensive evaluation of the agent system and generate insights.
        """
        evaluation_result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_performance": self._analyze_agent_performance(),
            "communication_patterns": self._analyze_communication_patterns(),
            "bottlenecks": self._identify_bottlenecks(),
            "suggested_agents": self._suggest_new_agents(),
            "improvement_suggestions": self._suggest_improvements()
        }
        
        # Generate visualization if enough data exists
        if len(self.communication_log) > 10:
            self._visualize_agent_network()
            
        return evaluation_result
    
    def _analyze_agent_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics for each agent"""
        result = {}
        
        for agent_name, metrics in self.agent_metrics.items():
            # Calculate success rate
            total_tasks = metrics["tasks_completed"] + metrics["failures"]
            success_rate = (metrics["tasks_completed"] / total_tasks) * 100 if total_tasks > 0 else 0
            
            # Calculate efficiency score (normalized between 0-100)
            efficiency_factors = [
                success_rate,
                100 * (1.0 / (1.0 + metrics["avg_response_time"])),  # Lower time is better
                10 * metrics["successful_collaborations"]  # Reward collaborations
            ]
            efficiency_score = sum(efficiency_factors) / len(efficiency_factors)
            
            result[agent_name] = {
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(metrics["avg_response_time"], 2),
                "efficiency_score": round(efficiency_score, 2),
                "tasks_handled": total_tasks,
                "specialization": self._determine_agent_specialization(agent_name)
            }
        
        return result
    
    def _determine_agent_specialization(self, agent_name: str) -> Dict[str, float]:
        """Determine what an agent specializes in based on task distribution"""
        specialization = {}
        task_counts = self.agent_task_distribution[agent_name]
        total_tasks = sum(task_counts.values())
        
        if total_tasks == 0:
            return {"unknown": 1.0}
            
        for task_type, count in task_counts.items():
            specialization[task_type] = count / total_tasks
            
        return specialization
    
    def _analyze_communication_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in inter-agent communications"""
        if not self.communication_log:
            return {"status": "insufficient_data"}
            
        # Identify most active communicators
        sender_counts = defaultdict(int)
        recipient_counts = defaultdict(int)
        message_types = defaultdict(int)
        
        for entry in self.communication_log:
            sender_counts[entry["sender"]] += 1
            recipient_counts[entry["recipient"]] += 1
            message_types[entry["message_type"]] += 1
        
        # Analyze communication chains
        chains = self._identify_communication_chains()
        
        return {
            "most_active_senders": dict(sorted(sender_counts.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]),
            "most_common_recipients": dict(sorted(recipient_counts.items(), 
                                          key=lambda x: x[1], reverse=True)[:5]),
            "message_type_distribution": dict(sorted(message_types.items(), 
                                             key=lambda x: x[1], reverse=True)),
            "common_communication_chains": chains,
            "communication_volume": len(self.communication_log)
        }
    
    def _identify_communication_chains(self) -> List[Dict[str, Any]]:
        """Identify common sequences of agent communication"""
        chains = []
        
        # Find paths in the communication graph
        if len(self.communication_graph.nodes) >= 2:
            # Find the most common paths between agents
            for source in self.communication_graph.nodes:
                for target in self.communication_graph.nodes:
                    if source != target:
                        try:
                            paths = list(nx.all_simple_paths(
                                self.communication_graph, source, target, cutoff=3))
                            
                            if paths:
                                # Calculate path weight based on edge weights
                                for path in paths:
                                    weight = 0
                                    for i in range(len(path) - 1):
                                        weight += self.communication_graph[path[i]][path[i+1]]["weight"]
                                    
                                    chains.append({
                                        "path": path,
                                        "weight": weight
                                    })
                        except nx.NetworkXNoPath:
                            pass
        
        # Sort chains by weight and return top 10
        return sorted(chains, key=lambda x: x["weight"], reverse=True)[:10]
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify bottlenecks in the agent communication system"""
        bottlenecks = []
        
        # Bottleneck type 1: Agents with high incoming but low outgoing communications
        if len(self.communication_graph.nodes) > 0:
            for node in self.communication_graph.nodes:
                in_degree = self.communication_graph.in_degree(node, weight='weight')
                out_degree = self.communication_graph.out_degree(node, weight='weight')
                
                if in_degree > 3 * out_degree and in_degree > 5:
                    bottlenecks.append({
                        "agent": node,
                        "bottleneck_type": "communication_sink",
                        "severity": "high" if in_degree > 10 else "medium",
                        "in_degree": in_degree,
                        "out_degree": out_degree
                    })
        
        # Bottleneck type 2: Agents with high failure rates
        for agent_name, metrics in self.agent_metrics.items():
            total_tasks = metrics["tasks_completed"] + metrics["failures"]
            if total_tasks > 5 and metrics["failures"] / total_tasks > 0.3:
                bottlenecks.append({
                    "agent": agent_name,
                    "bottleneck_type": "high_failure_rate",
                    "severity": "critical" if metrics["failures"] / total_tasks > 0.5 else "high",
                    "failure_rate": metrics["failures"] / total_tasks
                })
        
        # Bottleneck type 3: Slow response times
        slow_agents = []
        for agent_name, metrics in self.agent_metrics.items():
            if metrics["avg_response_time"] > 5.0:  # Threshold for "slow"
                slow_agents.append((agent_name, metrics["avg_response_time"]))
        
        for agent_name, response_time in sorted(slow_agents, key=lambda x: x[1], reverse=True)[:3]:
            bottlenecks.append({
                "agent": agent_name,
                "bottleneck_type": "slow_response",
                "severity": "high" if response_time > 10.0 else "medium",
                "avg_response_time": response_time
            })
            
        return bottlenecks
    
    def _suggest_new_agents(self) -> List[Dict[str, Any]]:
        """Suggest new agent types or capabilities based on observed patterns"""
        suggestions = []
        
        # Analyze task types that don't have specialized agents
        agent_specializations = {}
        for agent_name in self.agent_metrics.keys():
            specialization = self._determine_agent_specialization(agent_name)
            # Consider an agent specialized if one task type accounts for >60% of its work
            primary_task = max(specialization.items(), key=lambda x: x[1]) if specialization else ("unknown", 0)
            if primary_task[1] > 0.6:
                agent_specializations[primary_task[0]] = agent_name
        
        # Find task types without specialized agents
        all_task_types = set()
        for agent, task_dist in self.agent_task_distribution.items():
            all_task_types.update(task_dist.keys())
        
        unspecialized_tasks = all_task_types - set(agent_specializations.keys())
        for task_type in unspecialized_tasks:
            # Only suggest if this task type appears multiple times
            task_count = sum(dist.get(task_type, 0) for dist in self.agent_task_distribution.values())
            if task_count >= 3:
                suggestions.append({
                    "suggestion_type": "new_agent",
                    "task_specialization": task_type,
                    "rationale": f"Task type '{task_type}' appears {task_count} times but has no specialized agent",
                    "priority": "high" if task_count > 10 else "medium"
                })
        
        # Suggest agents to handle common bottlenecks
        bottlenecks = self._identify_bottlenecks()
        communication_bottlenecks = [b for b in bottlenecks if b["bottleneck_type"] == "communication_sink"]
        
        if communication_bottlenecks:
            suggestions.append({
                "suggestion_type": "new_agent",
                "agent_role": "communication_router",
                "rationale": "Add an agent to efficiently route messages and prevent communication bottlenecks",
                "priority": "high" if any(b["severity"] == "high" for b in communication_bottlenecks) else "medium"
            })
        
        # Suggest monitoring agent if multiple high failure rates detected
        high_failure_bottlenecks = [b for b in bottlenecks if b["bottleneck_type"] == "high_failure_rate"]
        if len(high_failure_bottlenecks) >= 2:
            suggestions.append({
                "suggestion_type": "new_agent",
                "agent_role": "reliability_monitor",
                "rationale": "Add an agent to monitor and improve reliability of agent tasks",
                "priority": "critical" if any(b["severity"] == "critical" for b in high_failure_bottlenecks) else "high"
            })
            
        return suggestions
    
    def _suggest_improvements(self) -> List[Dict[str, Any]]:
        """Propose enhancements for better system performance"""
        suggestions = []
        
        # Suggestion 1: Improve delegation strategies
        if self.communication_graph and len(self.communication_graph.nodes) >= 3:
            # Check for centralization patterns
            centrality = nx.degree_centrality(self.communication_graph)
            most_central = max(centrality.items(), key=lambda x: x[1])
            
            if most_central[1] > 0.7:  # Highly centralized network
                suggestions.append({
                    "improvement_area": "delegation",
                    "suggestion": "Implement load balancing to reduce dependence on central agent",
                    "target_component": most_central[0],
                    "priority": "high",
                    "implementation_detail": "Add a task distribution algorithm that considers agent specialization and current workload"
                })
        
        # Suggestion 2: Improve decision-making
        high_failure_agents = []
        for agent, metrics in self.agent_metrics.items():
            total = metrics["tasks_completed"] + metrics["failures"]
            if total > 5 and metrics["failures"]/total > 0.3:
                high_failure_agents.append(agent)
        
        if high_failure_agents:
            suggestions.append({
                "improvement_area": "decision_making",
                "suggestion": "Implement feedback loops for agents with high failure rates",
                "target_agents": high_failure_agents,
                "priority": "critical" if len(high_failure_agents) > 1 else "high",
                "implementation_detail": "Add runtime feedback mechanism that adjusts agent behavior based on success/failure patterns"
            })
        
        # Suggestion 3: Improve multi-agent task management
        if len(self.agent_metrics) >= 3:
            collaboration_rates = {agent: metrics["successful_collaborations"] / max(1, metrics["tasks_completed"])
                                 for agent, metrics in self.agent_metrics.items()}
            avg_collaboration = sum(collaboration_rates.values()) / len(collaboration_rates)
            
            if avg_collaboration < 0.2:  # Low collaboration environment
                suggestions.append({
                    "improvement_area": "multi_agent_task_management",
                    "suggestion": "Enhance collaboration mechanisms between agents",
                    "priority": "medium",
                    "implementation_detail": "Implement a shared context mechanism for related tasks and add collaboration score metrics"
                })
        
        # Suggestion 4: Communication efficiency
        if self.communication_log and len(self.communication_log) > 20:
            avg_message_size = sum(entry["message_size"] for entry in self.communication_log) / len(self.communication_log)
            if avg_message_size > 1000:  # Large messages
                suggestions.append({
                    "improvement_area": "communication",
                    "suggestion": "Optimize message payloads for efficiency",
                    "priority": "medium",
                    "implementation_detail": "Implement message compression or reference-passing instead of full payload transmission"
                })
        
        return suggestions
    
    def _visualize_agent_network(self) -> str:
        """Generate a visualization of the agent communication network"""
        if not self.communication_graph or len(self.communication_graph.nodes) < 2:
            return ""
            
        try:
            plt.figure(figsize=(10, 8))
            
            # Create positions using spring layout
            pos = nx.spring_layout(self.communication_graph)
            
            # Get edge weights for line thickness
            edge_weights = [self.communication_graph[u][v]['weight'] for u, v in self.communication_graph.edges()]
            max_weight = max(edge_weights) if edge_weights else 1
            normalized_weights = [3 * w / max_weight for w in edge_weights]
            
            # Draw the network
            nx.draw_networkx_nodes(self.communication_graph, pos, node_size=500, 
                                  node_color='lightblue')
            nx.draw_networkx_edges(self.communication_graph, pos, width=normalized_weights, 
                                  edge_color='gray', arrows=True, arrowsize=15)
            nx.draw_networkx_labels(self.communication_graph, pos, font_size=10)
            
            # Edge labels showing communication count
            edge_labels = {(u, v): f"{d['weight']}" for u, v, d in self.communication_graph.edges(data=True)}
            nx.draw_networkx_edge_labels(self.communication_graph, pos, edge_labels=edge_labels)
            
            plt.title("Agent Communication Network")
            plt.axis('off')
            
            # Save visualization
            filename = f"agent_network_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.png"
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            plt.savefig(file_path)
            plt.close()
            
            return file_path
        except Exception as e:
            logger.error(f"Failed to generate visualization: {e}")
            return ""

    async def generate_report(self, format="markdown") -> str:
        """
        Generate a comprehensive report about the agent system performance.
        """
        evaluation = await self.run_system_evaluation()
        
        if format == "json":
            return json.dumps(evaluation, indent=2)
        
        # Generate markdown report
        report = [
            "# Cherry AI Multi-Agent System Evaluation",
            f"*Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            
            "## Agent Performance Summary",
            "| Agent | Tasks | Success Rate | Avg Response Time | Efficiency Score |",
            "|-------|-------|-------------|------------------|-----------------|"
        ]
        
        # Add performance metrics
        perf = evaluation["agent_performance"]
        for agent_name, metrics in perf.items():
            report.append(f"| {agent_name} | {metrics['tasks_handled']} | " +
                         f"{metrics['success_rate']}% | {metrics['avg_response_time']}s | " +
                         f"{metrics['efficiency_score']} |")
        
        # Communication patterns
        report.extend([
            "\n## Communication Patterns",
            f"Total communications: {evaluation['communication_patterns'].get('communication_volume', 0)}"
        ])
        
        # Bottlenecks 
        report.extend([
            "\n## System Bottlenecks",
            "The following bottlenecks were identified:"
        ])
        
        for bottleneck in evaluation["bottlenecks"]:
            report.append(f"- **{bottleneck['agent']}**: {bottleneck['bottleneck_type']} " +
                         f"(Severity: {bottleneck['severity']})")
        
        # Suggested new agents
        if evaluation["suggested_agents"]:
            report.extend([
                "\n## Suggested New Agents", 
            ])
            
            for suggestion in evaluation["suggested_agents"]:
                if "agent_role" in suggestion:
                    report.append(f"- **{suggestion['agent_role']}** ({suggestion['priority']}): {suggestion['rationale']}")
                else:
                    report.append(f"- **{suggestion['task_specialization']} specialist** ({suggestion['priority']}): {suggestion['rationale']}")
        
        # Improvement suggestions
        report.extend([
            "\n## System Improvement Recommendations"
        ])
        
        for improvement in evaluation["improvement_suggestions"]:
            report.append(f"- **{improvement['improvement_area']}** ({improvement['priority']}): {improvement['suggestion']}")
            report.append(f"  - Implementation: {improvement['implementation_detail']}")
        
        # Add visualization reference if available
        viz_path = self._visualize_agent_network()
        if viz_path:
            report.append("\n## System Visualization")
            report.append(f"Communication network visualization: `{viz_path}`")
            
        return "\n".join(report)


# Middleware to intercept and log all agent communications
async def communication_logger_middleware(message, next_handler):
    """Middleware that logs agent communications for analysis"""
    evaluator = get_evaluator()
    await evaluator.log_communication(message)
    return await next_handler(message)


# Singleton pattern to access the evaluator
_evaluator_instance = None

def get_evaluator():
    """Get the singleton instance of AgentSystemEvaluator"""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = AgentSystemEvaluator()
    return _evaluator_instance


# Decorator to track task execution metrics
def track_task_execution(func):
    """Decorator that tracks task execution time and results"""
    async def wrapper(self, task_data, *args, **kwargs):
        start_time = datetime.datetime.now()
        try:
            result = await func(self, task_data, *args, **kwargs)
            success = "error" not in result
        except Exception:
            success = False
            raise
        finally:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            evaluator = get_evaluator()
            await evaluator.log_task_completion(
                self.name, task_data, execution_time, success
            )
        return result
    return wrapper