"""
Command-line interface for data management tasks.
"""
import argparse
import sys
import json
from typing import Dict, Any, Optional, List

from cherry.data_management.archivers.vector_archiver import archive_old_vectors
from cherry.data_management.scheduler import setup_archival_scheduler
from logger import get_logger

logger = get_logger(__name__)

def archive_command(args):
    """Run the archival command."""
    result = archive_old_vectors(args.index, args.months)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Archival process completed")
        print(f"Found: {result.get('found_vectors', 0)} vectors older than {args.months} months")
        print(f"Archived: {result.get('archived_vectors', 0)} vectors to PostgreSQL")
        print(f"Deleted: {result.get('deleted_vectors', 0)} vectors from Pinecone")
        print(f"Errors: {result.get('errors', 0)}")
        print(f"Time taken: {result.get('elapsed_seconds', 0):.2f} seconds")
        
def schedule_command(args):
    """Run the schedule command."""
    print(f"Setting up archival scheduler for index {args.index}")
    print(f"Will run daily at {args.hour:02d}:{args.minute:02d}")
    scheduler = setup_archival_scheduler(args.index, args.hour, args.minute)
    
    if args.run_now:
        print("Running initial archival now...")
        result = scheduler.run_now()
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Initial archival completed")
            print(f"Found: {result.get('found_vectors', 0)} vectors")
            print(f"Archived: {result.get('archived_vectors', 0)} vectors")
            print(f"Deleted: {result.get('deleted_vectors', 0)} vectors")
    
    # Keep running until interrupted
    try:
        print("Scheduler is running. Press Ctrl+C to stop.")
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Cherry Data Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive old vectors")
    archive_parser.add_argument("index", help="Pinecone index name")
    archive_parser.add_argument("--months", type=int, default=6, help="Archive vectors older than this many months")
    archive_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    archive_parser.set_defaults(func=archive_command)
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Schedule archival tasks")
    schedule_parser.add_argument("index", help="Pinecone index name")
    schedule_parser.add_argument("--hour", type=int, default=2, help="Hour of day to run (24-hour format)")
    schedule_parser.add_argument("--minute", type=int, default=0, help="Minute of hour to run")
    schedule_parser.add_argument("--run-now", action="store_true", help="Run archival immediately in addition to scheduling")
    schedule_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    schedule_parser.set_defaults(func=schedule_command)
    
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
        
    args.func(args)

if __name__ == "__main__":
    main()
