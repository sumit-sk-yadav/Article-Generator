"""Crew execution logic with checkpoint support"""
import time
from crewai import Crew, Process
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from src.checkpoint_manager import CheckpointManager
from src.agents import create_planner_agent, create_writer_agent, create_editor_agent
from src.tasks import create_plan_task, create_write_task, create_edit_task
from config import CREW_MAX_RPM, RETRY_MULTIPLIER, RETRY_MIN_WAIT, RETRY_MAX_WAIT, RETRY_MAX_ATTEMPTS, RETRY_DELAY


class CrewManager:
    """Manages crew execution with checkpoint support"""
    
    def __init__(self):
        self.checkpoint_manager = CheckpointManager()
        self.task_sequence = ['plan', 'write', 'edit']
    
    def _task_callback(self, task_output):
        """
        Callback function that runs after each task completes.
        Saves checkpoint for the completed task.
        """
        task_name = task_output.name if hasattr(task_output, 'name') else "unknown"
        output_str = str(task_output.raw) if hasattr(task_output, 'raw') else str(task_output)
        
        # Map task descriptions to checkpoint names
        if "Prioritize the latest trends" in str(task_output.description):
            checkpoint_name = 'plan'
        elif "Use the content plan to craft" in str(task_output.description):
            checkpoint_name = 'write'
        elif "Proofread the given blog post" in str(task_output.description):
            checkpoint_name = 'edit'
        else:
            checkpoint_name = task_name
        
        # Save checkpoint
        self.checkpoint_manager.save_checkpoint(
            checkpoint_name, 
            output_str,
            agent_name=task_output.agent if hasattr(task_output, 'agent') else None
        )
        
        print(f"✅ Task completed and checkpointed: {checkpoint_name}")
        return task_output
    
    def run_crew(self, topic, groq_api_key, tavily_api_key, force_restart=False):
        """
        Run crew with in-memory checkpoints (no file saving)
        
        Args:
            topic: Blog topic
            groq_api_key: Groq API key for LLM
            tavily_api_key: Tavily API key for search
            force_restart: Clear checkpoints and start fresh
        
        Returns:
            str: Final article content
        """
        # Set API keys in environment for this execution
        import os
        os.environ["GROQ_API_KEY"] = groq_api_key
        os.environ["TAVILY_API_KEY"] = tavily_api_key
        
        # Clear memory if force restart
        if force_restart:
            self.checkpoint_manager.clear_checkpoints()
            print("🔄 Starting fresh (memory cleared)")
        
        # Check for existing in-memory checkpoints
        last_completed = self.checkpoint_manager.get_last_completed_task(self.task_sequence)
        
        if last_completed:
            print(f"📌 Resuming from last checkpoint: {last_completed}")
            
            # If all tasks complete, return final result
            if last_completed == 'edit':
                final_checkpoint = self.checkpoint_manager.load_checkpoint('edit')
                result = final_checkpoint['output']
                print("✅ All tasks already completed (from memory)")
                return result
            
            # If partially complete, we'll still run the crew but checkpoints are available
            print(f"⚠️  Note: Partial checkpoints exist. Crew will re-run but can use cached data.")
        else:
            print("🚀 Starting crew from beginning")
        
        # Create agents
        planner = create_planner_agent()
        writer = create_writer_agent()
        editor = create_editor_agent()
        
        # Create tasks
        plan_task = create_plan_task(planner)
        write_task = create_write_task(writer, plan_task)
        edit_task = create_edit_task(editor, write_task)
        
        # Set callbacks for each task
        plan_task.callback = self._task_callback
        write_task.callback = self._task_callback
        edit_task.callback = self._task_callback
        
        # Configure crew
        crew = Crew(
            agents=[planner, writer, editor],
            tasks=[plan_task, write_task, edit_task],
            process=Process.sequential,
            max_rpm=CREW_MAX_RPM,
            verbose=True  # Enable verbose logging to see progress
        )
        
        try:
            print(f"🤖 Running crew for topic: {topic}")
            result = crew.kickoff(inputs={"topic": topic})
            
            print("✅ Crew execution completed successfully!")
            return result
            
        except Exception as e:
            print(f"❌ Error during execution: {str(e)}")
            
            # Show which checkpoints were saved before failure
            saved_checkpoints = self.checkpoint_manager.get_all_checkpoints()
            if saved_checkpoints:
                print(f"💾 Checkpoints preserved: {list(saved_checkpoints.keys())}")
            else:
                print("💾 No checkpoints were saved before failure")
            
            raise
    
    @retry(
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        retry=retry_if_exception_type((Exception,))
    )
    def run_with_retry(self, topic, groq_api_key, tavily_api_key, force_restart=False):
        """Execute crew with retry logic"""
        time.sleep(RETRY_DELAY)
        return self.run_crew(topic, groq_api_key, tavily_api_key, force_restart)
    
    def get_checkpoints(self):
        """Get all checkpoints for display"""
        return self.checkpoint_manager.get_all_checkpoints()
