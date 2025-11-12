"""Crew management with multi-provider support"""
import os
from crewai import Crew, Process
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError
import time
import re

from src.agents import create_planner_agent, create_writer_agent, create_editor_agent
from src.tasks import create_plan_task, create_write_task, create_edit_task
from src.checkpoint_manager import CheckpointManager
from config import (
    RETRY_MULTIPLIER, RETRY_MIN_WAIT, RETRY_MAX_WAIT, 
    RETRY_MAX_ATTEMPTS, RETRY_DELAY, CREW_MAX_RPM
)


class CrewManager:
    """Manages the content generation crew with multi-provider support"""
    
    def __init__(self):
        self.checkpoint_manager = CheckpointManager()
        self.crew = None
    
    def get_checkpoints(self):
        """Get all checkpoints"""
        return self.checkpoint_manager.get_all_checkpoints()
    
    def _setup_crew(self, provider: str, llm_api_key: str, tavily_api_key: str):
        """Set up the crew with agents and tasks"""
        # Set API keys based on provider
        provider_env_map = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "cerebras": "CEREBRAS_API_KEY"
        }
        
        os.environ[provider_env_map[provider]] = llm_api_key
        os.environ['TAVILY_API_KEY'] = tavily_api_key
        
        # Create agents
        planner = create_planner_agent()
        writer = create_writer_agent()
        editor = create_editor_agent()
        
        # Create tasks
        plan_task = create_plan_task(planner)
        write_task = create_write_task(writer, plan_task)
        edit_task = create_edit_task(editor, write_task)
        
        # Create crew
        self.crew = Crew(
            agents=[planner, writer, editor],
            tasks=[plan_task, write_task, edit_task],
            process=Process.sequential,
            verbose=True,
            max_rpm=CREW_MAX_RPM,
        )
        
        return plan_task, write_task, edit_task
    
    def _clean_output(self, text: str) -> str:
        """Remove any thinking tags or internal monologue from output"""
        # Remove <think>...</think> blocks
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'</?think>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _execute_task_with_checkpoint(self, task_name: str, agent, task_obj, context_output=None):
        """Execute a single task and save checkpoint"""
        try:
            print(f"\n🚀 Executing {task_name} task...")
            
            if context_output:
                result = agent.execute_task(task_obj, context=context_output)
            else:
                result = agent.execute_task(task_obj)
            
            # Clean output
            cleaned_result = self._clean_output(result)
            
            # Save checkpoint
            self.checkpoint_manager.save_checkpoint(
                task_name=task_name,
                output=cleaned_result,
                agent_name=agent.role
            )
            
            print(f"✅ {task_name} task completed")
            return cleaned_result
            
        except RateLimitError as e:
            print(f"⏸️ Rate limit hit during {task_name} task")
            raise e
    
    @retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=RETRY_MULTIPLIER,
            min=RETRY_MIN_WAIT,
            max=RETRY_MAX_WAIT
        ),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=lambda retry_state: print(
            f"⏳ Rate limit hit. Retrying in {retry_state.next_action.sleep} seconds... "
            f"(Attempt {retry_state.attempt_number}/{RETRY_MAX_ATTEMPTS})"
        )
    )
    def run_with_retry(self, topic: str, provider: str, llm_api_key: str, 
                    tavily_api_key: str, force_restart: bool = False):
        """Run crew with automatic retry and task-level resumption"""
        
        # Set the topic for checkpoint management
        self.checkpoint_manager.set_topic(topic)
    
        if force_restart:
            print("🔄 Force restart enabled - clearing all checkpoints")
            self.checkpoint_manager.clear_checkpoints(topic)  # Clear only this topic's checkpoints
    
        
        # Setup crew with selected provider
        plan_task, write_task, edit_task = self._setup_crew(provider, llm_api_key, tavily_api_key)
        planner = create_planner_agent()
        writer = create_writer_agent()
        editor = create_editor_agent()
        
        print(f"🚀 Using {provider.upper()} as LLM provider")
        
        try:
            # Task 1: Planning
            if self.checkpoint_manager.has_checkpoint('plan'):
                print("📋 Plan task already completed - using checkpoint")
                plan_output = self.checkpoint_manager.get_checkpoint('plan')['output']
            else:
                plan_output = self._execute_task_with_checkpoint('plan', planner, plan_task)
                time.sleep(RETRY_DELAY)
            
            # Task 2: Writing
            if self.checkpoint_manager.has_checkpoint('write'):
                print("✏️ Write task already completed - using checkpoint")
                write_output = self.checkpoint_manager.get_checkpoint('write')['output']
            else:
                write_output = self._execute_task_with_checkpoint('write', writer, write_task, context_output=plan_output)
                time.sleep(RETRY_DELAY)
            
            # Task 3: Editing
            if self.checkpoint_manager.has_checkpoint('edit'):
                print("📝 Edit task already completed - using checkpoint")
                edit_output = self.checkpoint_manager.get_checkpoint('edit')['output']
            else:
                edit_output = self._execute_task_with_checkpoint('edit', editor, edit_task, context_output=write_output)
            
            print("\n✅ All tasks completed successfully!")
            return edit_output
            
        except RateLimitError as e:
            latest = self.checkpoint_manager.get_latest_completed_task()
            if latest:
                print(f"\n⏸️ Execution paused due to rate limit. Progress saved up to: {latest}")
                print("💾 Run again to resume from the last checkpoint")
            raise e
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            latest = self.checkpoint_manager.get_latest_completed_task()
            if latest:
                print(f"💾 Progress saved up to: {latest}")
            raise e
