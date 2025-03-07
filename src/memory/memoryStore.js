const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, "../../tmp/memory");
const MEMORY_FILE = path.join(MEMORY_DIR, "service-memory.json");
const MAX_SHORT_TERM_ENTRIES = 50;

// Ensure the memory file exists
function ensureMemoryFile() {
  if (!fs.existsSync(MEMORY_DIR)) {
    fs.mkdirSync(MEMORY_DIR, { recursive: true });
  }
  if (!fs.existsSync(MEMORY_FILE)) {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify({ shortTerm: [], longTerm: [] }));
  }
}

function loadMemory() {
  ensureMemoryFile();
  try {
    const data = fs.readFileSync(MEMORY_FILE, "utf8");
    return JSON.parse(data);
  } catch (error) {
    console.error("Error reading memory file:", error);
    return { shortTerm: [], longTerm: [] };
  }
}

function saveMemory(memory) {
  ensureMemoryFile();
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2));
}

class MemoryStore {
  constructor(maxEntries = MAX_SHORT_TERM_ENTRIES) {
    this.maxEntries = maxEntries;
    this.memory = loadMemory();
  }

  /**
   * Adds a new entry to short-term memory and auto-summarizes if needed.
   * @param {Object} entry - The memory entry. e.g., { type, content, tags }.
   * @returns {string} The unique id of the entry.
   */
  addEntry(entry) {
    // Assign a unique id and timestamp to the entry.
    entry.id = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    entry.timestamp = new Date().toISOString();

    // Persist the entry in short-term memory.
    this.memory.shortTerm.push(entry);

    // Check whether we have exceeded our threshold.
    if (this.memory.shortTerm.length > this.maxEntries) {
      this.summarizeShortTerm();
    }

    saveMemory(this.memory);
    return entry.id;
  }

  /**
   * Retrieves memory entries (from both short-term and long-term) matching the filter function.
   * @param {Function} filterFn - A function that returns a boolean (entry) => boolean.
   * @returns {Array} Filtered memory entries.
   */
  getRelevantEntries(filterFn) {
    return [...this.memory.shortTerm, ...this.memory.longTerm].filter(filterFn);
  }

  /**
   * Summarizes the current short-term memory and archives it into long-term memory.
   * In a real-world scenario, you might want a more comprehensive summarization using NLP, etc.
   */
  summarizeShortTerm() {
    const summary = {
      id: Date.now() + '-' + Math.random().toString(36).substr(2, 9),
      summaryText: `Summarized ${this.memory.shortTerm.length} short-term entries.`,
      details: this.memory.shortTerm.map(e => ({
        id: e.id,
        snippet: JSON.stringify(e).slice(0, 50)
      })),
      timestamp: new Date().toISOString()
    };

    // Archive the summary in long-term memory.
    this.memory.longTerm.push(summary);
    // Clear the short-term memory.
    this.memory.shortTerm = [];
  }
}

module.exports = new MemoryStore();
