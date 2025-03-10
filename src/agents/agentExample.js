const memoryStore = require('../memory/memoryStore');

function processAndStore(data) {
  // Process the provided data...
  const entry = {
    type: 'processing_event',
    content: data,
    tags: ['analysis', 'event']
  };
  memoryStore.addEntry(entry);
  console.log('Memory updated with entry id:', entry.id);
}

module.exports = processAndStore;
