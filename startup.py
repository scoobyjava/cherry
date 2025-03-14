def __init__(self, config_path: str = 'config.json'):
    """Initialize the startup manager with configuration."""
    self.config_path = config_path
    self.config = {}
    self.services_status = {
        "environment_variables": {},
        "apis": {},
        "azure": {},
        "docker": {},
        "ai_assistants": {},
        "python_packages": {},
        "orchestrator": False
    }
    self.orchestrator = None
    self.recovery_actions = []


def load_configuration(self) -> bool:
    """Load configuration from the specified path."""
    try:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_file:
                self.config = json.load(config_file)
            logger.info(f"Configuration loaded from {self.config_path}")
            return True
        else:
            logger.warning(
                f"Configuration file not found at {self.config_path}")
            # Create default configuration
            self.config = {
                "required_env_vars": [
                    "OPENAI_API_KEY",
                    "AZURE_CONNECTION_STRING",
                    "CHERRY_ENV",
                    "CODY_API_KEY",
                    "CODEIUM_API_KEY",
                    "TABNINE_API_KEY"
                ],
                "apis": {
                    "openai": {"test_url": "https://api.openai.com/v1/models"},
                    "azure_openai": {"test_url": "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments?api-version=2023-05-15"}
                },
                "azure_services": ["storage", "cognitive", "functions"],
                "docker_services": ["tabnine", "elasticsearch", "redis"],
                "ai_assistants": ["cody", "codeium", "tabnine"],
                "required_packages": ["networkx", "openai", "azure-storage-blob", "requests"]
            }
            # Save default configuration
            with open(self.config_path, 'w') as config_file:
                json.dump(self.config, config_file, indent=2)
            logger.info(f"Created default configuration at {self.config_path}")
            return True
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return False


def check_environment_variables(self) -> Dict[str, bool]:
    """Check if required environment variables are set."""
    required_vars = self.config.get("required_env_vars", [
        "OPENAI_API_KEY",
        "AZURE_CONNECTION_STRING",
        "CHERRY_ENV",
        "CODY_API_KEY",
        "CODEIUM_API_KEY",
        "TABNINE_API_KEY"
    ])

    results = {}
    for var in required_vars:
        exists = var in os.environ and os.environ[var].strip() != ""
        results[var] = exists
        if not exists:
            logger.warning(f"Environment variable {var} is not set")
            self.recovery_actions.append(
                f"export {var}=your_{var.lower()}_value")

    return results


def check_api_connections(self) -> Dict[str, bool]:
    """Check API connections."""
    api_configs = self.config.get("api_connections", {
        "openai": {
            "api_key_var": "OPENAI_API_KEY",
            "test_url": "https://api.openai.com/v1/engines"
        },
        "github": {
            "api_key_var": "GITHUB_TOKEN",
            "test_url": "https://api.github.com/user"
        }
    })
    results = {}

    for api_name, api_config in api_configs.items():
        try:
            # Get API key from environment
            api_key_var = api_config.get("api_key_var", f"{api_name.upper()}_API_KEY")
            api_key = os.environ.get(api_key_var, "")

            # Prepare headers
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

            # Test connection
            logger.info(f"Testing connection to {api_name} API...")
            response = requests.get(
                api_config["test_url"], headers=headers, timeout=10)

            if response.status_code < 400:  # Accept 2xx and 3xx responses
                logger.info(
                    f"API {api_name} is accessible (Status: {response.status_code})")
                results[api_name] = True
            else:
                logger.warning(
                    f"API {api_name} returned status code {response.status_code}")
                results[api_name] = False
                self.recovery_actions.append(
                    f"Check {api_key_var} environment variable and API access")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to API {api_name}: {e}")
            results[api_name] = False
            self.recovery_actions.append(
                f"Check internet connection and {api_name} API availability")
        except Exception as e:
            logger.error(f"Unexpected error checking API {api_name}: {e}")
            results[api_name] = False

    return results

def monitor_api_connections(self, interval: int = 300) -> None:
    """
    Start a background thread to periodically monitor API connections.

    Args:
        interval: Time between checks in seconds (default: 5 minutes)
    """
    def _monitor_loop():
        while self.monitoring_active:
            logger.info("Running periodic API connection check...")
            api_results = self.check_api_connections()

            # Log any failures
            failed_apis = [api for api, status in api_results.items() if not status]
            if failed_apis:
                logger.warning(f"API connection issues detected: {', '.join(failed_apis)}")

                # Try to recover OpenAI specifically
                if "openai" in failed_apis:
                    try:
                        logger.info("Attempting to reinitialize OpenAI client...")
                        import openai
                        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
                        openai.Engine.list()
                        logger.info("OpenAI re-initialization successful.")
                    except Exception as e:
                        logger.error(f"OpenAI re-initialization failed: {e}")
            else:
                logger.info("All API connections are healthy.")

            time.sleep(interval)

    self.monitoring_active = True
    self.monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
    self.monitor_thread.start()
    logger.info(f"API monitoring started (interval: {interval}s)")

def stop_monitoring(self) -> None:
    """Stop the API monitoring thread."""
    if hasattr(self, 'monitoring_active'):
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
            logger.info("API monitoring stopped.")


def check_azure_connections(self) -> Dict[str, bool]:
    """Check Azure connections."""
    azure_services = self.config.get(
        "azure_services", ["storage", "cognitive", "functions"])
    results = {}

    for service in azure_services:
        try:
            # Check if the connection string exists
            conn_var = f"AZURE_{service.upper()}_CONNECTION_STRING"
            conn_string = os.environ.get(conn_var, "")

            if not conn_string:
                logger.warning(f"Azure {service} connection string not found")
                results[service] = False
                self.recovery_actions.append(
                    f"Set {conn_var} environment variable")
                continue

            # For Azure Storage, we can do a more thorough check
            if service == "storage" and conn_string:
                try:
                    from azure.storage.blob import BlobServiceClient
                    blob_service = BlobServiceClient.from_connection_string(
                        conn_string)
                    # Just list containers to verify connection
                    list(blob_service.list_containers(max_results=1))
                    logger.info(f"Azure {service} connection verified")
                    results[service] = True
                except Exception as e:
                    logger.error(f"Azure {service} connection failed: {e}")
                    results[service] = False
                    self.recovery_actions.append(
                        f"Check {conn_var} value and network connectivity")
            else:
                # For other services, just check if the connection string exists
                logger.info(
                    f"Azure {service} connection string exists (not verified)")
                results[service] = True
        except Exception as e:
            logger.error(f"Error checking Azure {service}: {e}")
            results[service] = False
            self.recovery_actions.append(f"Install Azure SDK for {service}")

    return results


def check_docker_services(self) -> Dict[str, bool]:
    """Check if required Docker services are running."""
    docker_services = self.config.get(
        "docker_services", ["tabnine", "elasticsearch", "redis"])
    results = {}

    # First check if Docker is running
    try:
        subprocess.run(["docker", "info"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        docker_running = True
    except (subprocess.SubprocessError, FileNotFoundError):
        docker_running = False
        logger.error("Docker is not running or not installed")
        self.recovery_actions.append("Start Docker Desktop or install Docker")

    if not docker_running:
        # Mark all services as down if Docker itself isn't running
        for service in docker_services:
            results[service] = False
        return results

    # Check each service
    for service in docker_services:
        try:
            # Check if the container exists and is running
            cmd = ["docker", "ps", "--filter",
                   f"name={service}", "--format", "{{.Status}}"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if "Up" in result.stdout:
                logger.info(f"Docker service {service} is running")
                results[service] = True
            else:
                # Check if container exists but is stopped
                cmd = ["docker", "ps", "-a", "--filter",
                       f"name={service}", "--format", "{{.Status}}"]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.stdout.strip():
                    logger.warning(
                        f"Docker service {service} exists but is not running")
                    results[service] = False
                    self.recovery_actions.append(f"docker start {service}")
                else:
                    logger.warning(f"Docker service {service} does not exist")
                    results[service] = False
                    self.recovery_actions.append(
                        f"Check docker-compose.yml for {service} configuration")
        except Exception as e:
            logger.error(f"Error checking Docker service {service}: {e}")
            results[service] = False

    return results


def check_ai_assistants(self) -> Dict[str, bool]:
    """Check if AI coding assistants are properly configured."""
    ai_assistants = self.config.get(
        "ai_assistants", ["cody", "codeium", "tabnine"])
    results = {}

    for assistant in ai_assistants:
        try:
            # Check if the API key exists
            api_key_var = f"{assistant.upper()}_API_KEY"
            api_key = os.environ.get(api_key_var, "")

            if not api_key:
                logger.warning(f"{assistant} API key not found")
                results[assistant] = False
                self.recovery_actions.append(
                    f"Set {api_key_var} environment variable")
                continue

            # Check for extension configuration files
            if assistant == "cody":
                config_path = os.path.expanduser("~/.config/cody/config.json")
                if os.path.exists(config_path):
                    logger.info(f"{assistant} configuration found")
                    results[assistant] = True
                else:
                    logger.warning(f"{assistant} configuration not found")
                    results[assistant] = False
                    self.recovery_actions.append(
                        f"Configure {assistant} extension")

            elif assistant == "codeium":
                config_path = os.path.expanduser(
                    "~/.config/codeium/config.json")
                if os.path.
