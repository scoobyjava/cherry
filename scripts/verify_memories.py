import asyncio
import argparse
import json
import sys
import os
import logging
from pathlib import Path

# Ensure Cherry modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory_verification import verify_and_reconcile_memories

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("memory_verification.log")
    ]
)
logger = logging.getLogger("cherry.scripts.verify_memories")

async def main():
    parser = argparse.ArgumentParser(description="Verify and reconcile UIUXAgent memories in PostgreSQL and Pinecone")
    parser.add_argument("--verify-only", action="store_true", help="Only verify without reconciling")
    parser.add_argument("--output", "-o", help="Output file for verification results (JSON)")
    args = parser.parse_args()
    
    try:
        logger.info("Starting memory verification process")
        results = await verify_and_reconcile_memories()
        
        # Print summary to console
        verification = results["verification"]
        print("\n=== Memory Verification Results ===")
        print(f"Postgres memories: {verification['total_pg_memories']}")
        print(f"Pinecone memories: {verification['total_pinecone_memories']}")
        print(f"Missing in Pinecone: {len(verification['missing_in_pinecone'])}")
        print(f"Missing in PostgreSQL: {len(verification['missing_in_postgres'])}")
        
        if results.get("reconciliation"):
            recon = results["reconciliation"]
            print("\n=== Reconciliation Results ===")
            print(f"Fixed in Pinecone: {recon['fixed_in_pinecone']}")
            print(f"Fixed in PostgreSQL: {recon['fixed_in_postgres']}")
            print(f"Failed fixes: {recon['failed_fixes']}")
        
        # Save to file if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")
        
        logger.info("Memory verification process completed")
            
    except Exception as e:
        logger.error(f"Error during memory verification: {e}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
