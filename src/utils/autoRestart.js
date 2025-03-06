require("./utils/autoRestart");

const { exec } = require("child_process");
const logger = require("../logger");

/**
 * Check if a process is running.
 * You may need to adjust the command and grep filter based on your actual process names.
 */
function checkProcess(processName, callback) {
  exec(`pgrep -f ${processName}`, (error, stdout, stderr) => {
    if (error || !stdout.trim()) {
      callback(false);
    } else {
      callback(true);
    }
  });
}

/**
 * Restart a process by running its start command.
 */
function restartProcess(processName, startCommand) {
  exec(startCommand, (error, stdout, stderr) => {
    if (error) {
      logger.error(`Failed to restart ${processName}: ${error.message}`);
    } else {
      logger.info(`${processName} restarted successfully.`);
    }
  });
}

/**
 * Auto-restart check for a given process.
 */
function autoRestart(processName, startCommand) {
  checkProcess(processName, (isRunning) => {
    if (!isRunning) {
      logger.info(`${processName} not running. Attempting restart...`);
      restartProcess(processName, startCommand);
    } else {
      logger.info(`${processName} is running fine.`);
    }
  });
}

// Example: Scheduled checks for SonarQube and Cody: AI Code Assistant every 60 seconds
setInterval(() => {
  autoRestart("sonarqube", "docker start sonarqube_container"); // Adjust as needed
  autoRestart("cody", "systemctl start cody-ai"); // Adjust as needed
}, 60000); // 60 seconds

module.exports = { autoRestart };
