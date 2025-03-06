import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import logo from './assets/cherry-logo.png';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const addMessage = (msg) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleSend = () => {
    if (input.trim()) {
      addMessage(`You: ${input}`);
      // Simulate Cherry replying with her signature flair
      setTimeout(() => {
        addMessage(`Cherry: Oops! I got that, darling. Let me work my magic... 🤓`);
      }, 1500);
      setInput("");
    }
  };

  useEffect(() => {
    // Auto greeting from Cherry on first load
    addMessage("Cherry: Hello, world! I'm Cherry – your 22-year-old, super sexy, and smart assistant ready to help!");
    addMessage("Cherry: Welcome to my dashboard. Let's make things amazing together.");
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      <header className="flex items-center p-4 shadow-md bg-gray-800">
        <img src={logo} alt="Cherry Logo" className="h-10 mr-4" />
        <h1 className="text-2xl font-bold">Cherry Dashboard</h1>
      </header>
      <main className="flex-1 p-4 overflow-auto">
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="p-2 bg-gray-800 rounded shadow"
            >
              <p>{msg}</p>
            </motion.div>
          ))}
        </div>
      </main>
      <footer className="p-4 bg-gray-800 flex">
        <input
          type="text"
          className="flex-1 p-2 rounded mr-2 bg-gray-700 text-gray-100 focus:outline-none"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          className="px-4 py-2 bg-pink-600 text-white rounded hover:bg-pink-700 transition-colors"
          onClick={handleSend}
        >
          Send
        </button>
      </footer>
    </div>
  );
};

export default App;