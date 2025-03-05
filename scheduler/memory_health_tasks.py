import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from utils.memory_verification import verify_and_reconcile_memories

logger = logging.getLogger("cherry.scheduler.memory_health")

class MemoryHealthScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.results_dir = Path("logs/memory_health")
        self.verification_interval_minutes = int(os.getenv("MEMORY_VERIFICATION_INTERVAL_MINUTES", "60"))
        
        # Create directory for storing verification results
        os.makedirs(self.results_dir, exist_ok=True)
    
    async def run_memory_verification(self):
        """Run the memory verification and reconciliation task."""
        logger.info("Running scheduled memory verification")
        
        try:
            start_time = datetime.utcnow()
            results = await verify_and_reconcile_memories()
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Add execution time to results
            results["execution_time_seconds"] = execution_time
            results["started_at"] = start_time.isoformat()
            results["completed_at"] = end_time.isoformat()
            
            # Save results to file
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
            result_file = self.results_dir / f"verification_{timestamp}.json"
            with open(result_file, "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Memory verification completed in {execution_time:.2f} seconds, results saved to {result_file}")
            
            # If reconciliation was performed, log a summary
            if results.get("reconciliation"):
                recon = results["reconciliation"]
                logger.info(f"Reconciliation summary: fixed {recon['fixed_in_pinecone']} in Pinecone, "
                           f"{recon['fixed_in_postgres']} in PostgreSQL, {recon['failed_fixes']} failures")
        
        except Exception as e:
            logger.error(f"Error during scheduled memory verification: {e}", exc_info=True)
    
    def start(self):
        """Start the memory health scheduler."""
        # Schedule the memory verification task
        self.scheduler.add_job(
            self.run_memory_verification,
            trigger=IntervalTrigger(minutes=self.verification_interval_minutes),
            id="memory_verification",
            name="UIUXAgent Memory Verification",
            replace_existing=True
        )
        
        # Also run immediately on startup
        self.scheduler.add_job(
            self.run_memory_verification,
            trigger="date",
            run_date=datetime.now() + timedelta(seconds=10),
            id="memory_verification_startup",
            name="Initial UIUXAgent Memory Verification"
        )
        
        self.scheduler.start()
        logger.info(f"Memory health scheduler started. Verification interval: {self.verification_interval_minutes} minutes")
    
    def stop(self):
        """Stop the memory health scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Memory health scheduler stopped")
