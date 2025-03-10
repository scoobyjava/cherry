const chalk = require('chalk');

const LEVELS = {
  info: 'INFO',
  error: 'ERROR',
  debug: 'DEBUG'
};

const useColor = process.env.NODE_ENV !== 'production';

function formatMessage(level, message, additional) {
  const baseLog = {
    level,
    message,
    timestamp: new Date().toISOString(),
    ...additional
  };
  return JSON.stringify(baseLog);
}

function log(level, message, additional = {}) {
  const output = formatMessage(level, message, additional);
  // Optionally, colorize output for non-production environments:
  if (useColor) {
    switch (level) {
      case LEVELS.error:
        console.error(chalk.red(output));
        break;
      case LEVELS.debug:
        console.debug(chalk.magenta(output));
        break;
      default:
        console.log(chalk.blue(output));
    }
  } else {
    console.log(output);
  }
}

module.exports = {
  info: (message, additional) => log(LEVELS.info, message, additional),
  error: (message, additional) => log(LEVELS.error, message, additional),
  debug: (message, additional) => log(LEVELS.debug, message, additional)
};
