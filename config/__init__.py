from .loader import ConfigLoader
from .models import AppConfig

# Create a singleton config instance
config = ConfigLoader().load_config()

# Export the config instance and relevant types
__all__ = ["config", "AppConfig"]
