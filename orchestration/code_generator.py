import asyncio
import logging
from cherry.coding.agent_system import CodeContext, CherryCodeOrchestrator
from cherry.core.task_scheduler import TaskScheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cherry-orchestrator")

class WebsiteOrchestrator:
    def __init__(self):
        self.scheduler = TaskScheduler()
        self.code_orchestrator = CherryCodeOrchestrator()
        self._setup_task_handlers()
        
    def _setup_task_handlers(self):
        self.scheduler.register_task_handler("generate_code", self.handle_code_generation_task)
        
    async def handle_code_generation_task(self, task_data):
        try:
            logger.info(f"Generating code for {task_data['file_path']}")
            
            context = CodeContext(
                project_name=task_data.get("project_name", "Cherry Website"),
                file_path=task_data["file_path"],
                language=task_data["language"],
                requirements=task_data["requirements"],
                context_files=task_data.get("context_files", {})
            )
            
            # Generate initial solution
            solution = await self.code_orchestrator.generate_solution(context)
            
            # Validate and improve if needed
            validation = await self.code_orchestrator.validate_solution(task_data["file_path"], context)
            
            if validation.score < 0.8:
                logger.info(f"Initial solution scored {validation.score}, improving...")
                solution = await self.code_orchestrator.improve_solution(task_data["file_path"], context)
                validation = await self.code_orchestrator.validate_solution(task_data["file_path"], context)
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(task_data["file_path"]), exist_ok=True)
            
            # Write solution to file
            with open(task_data["file_path"], "w") as f:
                f.write(solution.code)
            
            logger.info(f"Successfully generated {task_data['file_path']}")
            
            return {
                "status": "completed",
                "file_path": task_data["file_path"],
                "quality_score": validation.score,
                "issues_resolved": len(validation.issues)
            }
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return {
                "status": "failed",
                "file_path": task_data["file_path"],
                "error": str(e)
            }
    
    def schedule_website_components(self):
        """Schedule generation of all website components"""
        try:
            # Frontend core components
            self.scheduler.schedule_task({
                "type": "generate_code",
                "priority": 10,
                "data": {
                    "project_name": "Cherry Website",
                    "file_path": "frontend/components/Dashboard.jsx",
                    "language": "jsx",
                    "requirements": "Create a real-time performance dashboard component with metrics display, charts using recharts library, and filterable data tables. Include state management with React hooks."
                }
            })
            
            self.scheduler.schedule_task({
                "type": "generate_code",
                "priority": 9,
                "data": {
                    "project_name": "Cherry Website",
                    "file_path": "frontend/components/Navigation.jsx",
                    "language": "jsx",
                    "requirements": "Create a responsive navigation bar with the Cherry logo, links to Home, Features, Pricing, and Contact pages. Include a dark/light mode toggle."
                }
            })
            
            self.scheduler.schedule_task({
                "type": "generate_code",
                "priority": 8,
                "data": {
                    "project_name": "Cherry Website",
                    "file_path": "frontend/components/Footer.jsx",
                    "language": "jsx",
                    "requirements": "Create a footer with links to social media, contact information, and copyright notice."
                }
            })
            
            # Frontend pages
            self.scheduler.schedule_task({
                "type": "generate_code", 
                "priority": 7,
                "data": {
                    "project_name": "Cherry Website",
                    "file_path": "frontend/pages/Home.jsx",
                    "language": "jsx",
                    "requirements": "Create a landing page with hero section, feature highlights, testimonials section, and call-to-action buttons."
                }
            })
            
            # Backend API
            self.scheduler.schedule_task({
                "type": "generate_code",
                "priority": 6,
                "data": {
                    "project_name": "Cherry Website",
                    "file_path": "backend/api/user_routes.js",
                    "language": "javascript",
                    "requirements": "Create Express.js API routes for user authentication including login, registration, and profile management with JWT authentication."
                }
            })
            
            logger.info("Successfully scheduled all website components")
            
        except Exception as e:
            logger.error(f"Error scheduling tasks: {str(e)}")
    
    def run(self):
        """Run the orchestrator"""
        try:
            self.schedule_website_components()
            self.scheduler.run()
        except Exception as e:
            logger.error(f"Error running orchestrator: {str(e)}")
            
if __name__ == "__main__":
    orchestrator = WebsiteOrchestrator()
    orchestrator.run()
