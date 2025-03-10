const fs = require('fs');
const path = require('path');

const memoryLogPath = path.join(__dirname, '../src/logs/cherryMemory.log');

function readMemory() {
  if (!fs.existsSync(memoryLogPath)) {
    return '';
  }
  return fs.readFileSync(memoryLogPath, 'utf8');
}

function writeMemory(data) {
  fs.appendFileSync(memoryLogPath, data + "\n", 'utf8');
}

module.exports = { readMemory, writeMemory };

