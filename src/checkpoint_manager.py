"""Checkpoint management for crew execution"""
import json
from datetime import datetime
from typing import Dict, Any, Optional


class CheckpointManager:
    """Manages task checkpoints for resumable execution"""
    
    def __init__(self):
        self.checkpoints: Dict[str, Dict[str, Dict[str, Any]]] = {}  # topic -> task -> checkpoint
        self.current_topic: Optional[str] = None
    
    def set_topic(self, topic: str):
        """Set the current topic for checkpoint management"""
        self.current_topic = topic
        if topic not in self.checkpoints:
            self.checkpoints[topic] = {}
    
    def save_checkpoint(self, task_name: str, output: str, agent_name: str = None):
        """Save a task checkpoint with its output"""
        if not self.current_topic:
            print("⚠️ Warning: No topic set for checkpoint")
            return
        
        if self.current_topic not in self.checkpoints:
            self.checkpoints[self.current_topic] = {}
        
        self.checkpoints[self.current_topic][task_name] = {
            'output': output,
            'agent': agent_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed': True
        }
        print(f"✅ Checkpoint saved for task: {task_name} (topic: {self.current_topic})")
    
    def get_checkpoint(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific checkpoint for current topic"""
        if not self.current_topic or self.current_topic not in self.checkpoints:
            return None
        return self.checkpoints.get(self.current_topic, {}).get(task_name)
    
    def has_checkpoint(self, task_name: str) -> bool:
        """Check if a checkpoint exists for a task in current topic"""
        if not self.current_topic or self.current_topic not in self.checkpoints:
            return False
        checkpoint = self.checkpoints.get(self.current_topic, {}).get(task_name)
        return checkpoint is not None and checkpoint.get('completed', False)
    
    def get_all_checkpoints(self) -> Dict[str, Dict[str, Any]]:
        """Get all checkpoints for current topic"""
        if not self.current_topic:
            return {}
        return self.checkpoints.get(self.current_topic, {})
    
    def clear_checkpoints(self, topic: Optional[str] = None):
        """Clear checkpoints for a specific topic or current topic"""
        target_topic = topic or self.current_topic
        if target_topic and target_topic in self.checkpoints:
            del self.checkpoints[target_topic]
            print(f"🗑️ Checkpoints cleared for topic: {target_topic}")
        else:
            print("🗑️ No checkpoints to clear")
    
    def clear_all_checkpoints(self):
        """Clear all checkpoints for all topics"""
        self.checkpoints = {}
        self.current_topic = None
        print("🗑️ All checkpoints cleared")
    
    def get_latest_completed_task(self) -> Optional[str]:
        """Get the name of the last completed task for current topic"""
        if not self.current_topic or self.current_topic not in self.checkpoints:
            return None
        
        completed_tasks = [
            name for name, data in self.checkpoints[self.current_topic].items() 
            if data.get('completed')
        ]
        if not completed_tasks:
            return None
        
        # Assuming tasks are in order: plan -> write -> edit
        task_order = ['plan', 'write', 'edit']
        for task in reversed(task_order):
            if task in completed_tasks:
                return task
        return None
