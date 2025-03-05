"""
Command-line interface with error handling capabilities.
"""
import argparse
import logging
import sys
import json
from typing import Optional, Dict, Any

from cherry.core.orchestrator import Orchestrator
from cherry.core.errors import CherryError

logger = logging.getLogger(__name__)


def setup_error_handling_args(parser: argparse.ArgumentParser) -> None:
    """
    Add error handling related arguments to the parser.
    
    Args:
        parser: The argument parser to enhance
    """
    error_group = parser.add_argument_group('Error Handling')
    error_group.add_argument(
        '--max-retries', 
        type=int,
        default=3,
        help='Maximum number of retries for failed operations'
    )
    error_group.add_argument(
        '--retry-delay',
        type=float,
        default=1.0,
        help='Initial delay between retries in seconds'
    )
    error_group.add_argument(
        '--error-thresholds',
        type=str,
        help='JSON string of error type to threshold mappings'
    )
    error_group.add_argument(
        '--fallback-config',
        type=str,
        help='Path to JSON file with fallback agent configurations'
    )


def get_error_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Extract error handling configuration from command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Dictionary with error handling configuration
    """
    config = {
        'max_retries': args.max_retries,
        'retry_delay': args.retry_delay,
        'error_thresholds': {}
    }
    
    # Parse error thresholds if provided
    if args.error_thresholds:
        try:
            config['error_thresholds'] = json.loads(args.error_thresholds)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON provided for error thresholds, using defaults")
    
    # Load fallback configuration if provided
    if args.fallback_config:
        try:
            with open(args.fallback_config, 'r') as f:
                config['fallback_agents'] = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Failed to load fallback configuration: {str(e)}")
    
    return config


def main(args: Optional[list] = None) -> int:
    """
    Main entry point with error handling.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(description='Cherry Orchestrator CLI')
    # Add common arguments
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Increase verbosity')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    # Add error handling arguments
    setup_error_handling_args(parser)
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the orchestrator')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get orchestrator status')
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Set up logging based on verbosity
    log_level = [logging.WARNING, logging.INFO, logging.DEBUG][min(parsed_args.verbose, 2)]
    logging.basicConfig(level=log_level)
    
    # Process commands
    try:
        if parsed_args.command == 'start':
            # Initialize orchestrator with error handling config
            error_config = get_error_config(parsed_args)
            orchestrator = Orchestrator(config=error_config)
            # Start orchestrator
            logger.info("Starting orchestrator...")
            # Additional startup code...
            
        elif parsed_args.command == 'status':
            # Initialize orchestrator
            orchestrator = Orchestrator()
            # Get and display health status
            status = orchestrator.get_health_status()
            print(json.dumps(status, indent=2))
            
        else:
            parser.print_help()
            return 1
            
        return 0
        
    except CherryError as e:
        logger.error(f"Error: {str(e)}")
        if hasattr(e, 'details') and e.details:
            logger.debug(f"Error details: {e.details}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if parsed_args.verbose > 0:
            logger.exception("Exception details:")
        return 2


if __name__ == "__main__":
    sys.exit(main())
```