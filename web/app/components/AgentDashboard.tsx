'use client';

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Define agent type for Cherry
type Agent = {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'offline';
  lastActive: string;
  metrics: {
    queries: number;
    responses: number;
    avgResponseTime: number;
  };
};

// Simple WebSocket hook without extra production security features
const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [data, setData] = useState<any>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // Linear backoff for simplicity
  const getReconnectDelay = (attempt: number): number => {
    return 1000 * (attempt + 1);
  };

  const connect = useCallback(() => {
    // Close current socket, if any
    if (socketRef.current) {
      socketRef.current.close();
    }

    try {
      // Append a timestamp to avoid caching issues
      const wsUrl = `${url}${url.includes('?') ? '&' : '?'}t=${Date.now()}`;
      const socket = new WebSocket(wsUrl);

      socket.addEventListener('open', () => {
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        console.log('[Cherry] WebSocket connected');
      });

      socket.addEventListener('message', (event) => {
        try {
          if (typeof event.data === 'string') {
            const parsedData = JSON.parse(event.data);
            setData(parsedData);
          }
        } catch (error) {
          console.error('[Cherry] Error parsing message:', error);
        }
      });

      socket.addEventListener('close', () => {
        setIsConnected(false);
        console.log('[Cherry] WebSocket closed. Reconnecting…');
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = getReconnectDelay(reconnectAttemptsRef.current);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else {
          console.log('[Cherry] Maximum reconnect attempts reached.');
        }
      });

      socket.addEventListener('error', (error) => {
        console.error('[Cherry] WebSocket error:', error);
      });

      socketRef.current = socket;
    } catch (error) {
      console.error('[Cherry] Failed to connect to WebSocket:', error);
    }
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [connect]);

  // Simple send function (no message queuing)
  const sendData = useCallback((message: any) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn('[Cherry] Socket not open, message lost');
      return;
    }
    try {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      socketRef.current.send(payload);
    } catch (error) {
      console.error('[Cherry] Error sending message:', error);
    }
  }, []);

  return { isConnected, data, sendData };
};

// AgentDashboard component using Tailwind grid & Framer Motion animations
const AgentDashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { isConnected, data } = useWebSocket('ws://localhost:8000/ws/agents');

  // Initial fetch of agent data
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch('/api/agents');
        if (!res.ok) throw new Error('Failed to fetch agents.');
        const agentsData = await res.json();
        setAgents(agentsData);
      } catch (error) {
        console.error('[Cherry] Error fetching agents:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAgents();
  }, []);

  // Update agents on incoming WebSocket messages
  useEffect(() => {
    if (data && data.type === 'agent_update') {
      setAgents((prev) => {
        const updated = [...prev];
        const idx = updated.findIndex(agent => agent.id === data.agent.id);
        if (idx >= 0) {
          updated[idx] = { ...updated[idx], ...data.agent };
        } else {
          updated.push(data.agent);
        }
        return updated;
      });
    }
  }, [data]);

  // Framer Motion variants for card animation
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.1, duration: 0.5, ease: 'easeOut' }
    })
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-100">Cherry Agent Dashboard</h1>
        <div className="flex items-center space-x-2">
          <div className={`h-3 w-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-400">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <AnimatePresence>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.id}
              custom={index}
              initial="hidden"
              animate="visible"
              variants={cardVariants}
              className="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-pink-500 transition-colors duration-300"
            >
              <div className="p-5">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold text-white">{agent.name}</h2>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    agent.status === 'active' ? 'bg-green-500/20 text-green-400' :
                    agent.status === 'idle' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </span>
                </div>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-400">Last Active</p>
                    <p className="text-gray-300">{new Date(agent.lastActive).toLocaleString()}</p>
                  </div>
                  <div className="grid grid-cols-3 gap-3 pt-2">
                    <div className="bg-gray-700/50 p-2 rounded">
                      <p className="text-xs text-gray-400">Queries</p>
                      <p className="text-lg font-medium text-white">{agent.metrics.queries}</p>
                    </div>
                    <div className="bg-gray-700/50 p-2 rounded">
                      <p className="text-xs text-gray-400">Responses</p>
                      <p className="text-lg font-medium text-white">{agent.metrics.responses}</p>
                    </div>
                    <div className="bg-gray-700/50 p-2 rounded">
                      <p className="text-xs text-gray-400">Avg Time</p>
                      <p className="text-lg font-medium text-white">{agent.metrics.avgResponseTime}ms</p>
                    </div>
                  </div>
                </div>
              </div>
              <footer className="bg-gray-900 px-5 py-3 flex justify-between items-center">
                <button className="text-sm text-pink-400 hover:text-pink-300 transition-colors">
                  View Details
                </button>
                <button className="text-sm text-gray-400 hover:text-white transition-colors">
                  Manage
                </button>
              </footer>
            </motion.div>
          ))}
        </div>
      </AnimatePresence>

      {agents.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No agents available</p>
          <button className="mt-4 px-4 py-2 bg-pink-600 text-white rounded hover:bg-pink-700 transition-colors">
            Add Agent
          </button>
        </div>
      )}
    </div>
  );
};

export default AgentDashboard;