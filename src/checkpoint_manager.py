"""Checkpoint management for crew tasks"""
from datetime import datetime


class CheckpointManager:
    """Manages in-memory checkpoints for crew tasks"""
    
    def __init__(self):
        # Store checkpoints in memory
        self.checkpoints = {}
        
    def save_checkpoint(self, task_name, output, agent_name=None):
        """Save task output to memory instead of file"""
        checkpoint_data = {
            'task_name': task_name,
            'output': output,
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'output_length': len(str(output))
        }
        self.checkpoints[task_name] = checkpoint_data
        
        # Detailed logging
        print(f"\n{'='*60}")
        print(f"✓ CHECKPOINT SAVED: {task_name.upper()}")
        print(f"{'='*60}")
        print(f"Agent: {agent_name}")
        print(f"Timestamp: {checkpoint_data['timestamp']}")
        print(f"Output Length: {checkpoint_data['output_length']} characters")
        print(f"Preview: {str(output)[:100]}...")
        print(f"{'='*60}\n")
        
        return checkpoint_data

    
    def load_checkpoint(self, task_name):
        """Load checkpoint from memory"""
        return self.checkpoints.get(task_name)
    
    def checkpoint_exists(self, task_name):
        """Check if checkpoint exists in memory"""
        return task_name in self.checkpoints
    
    def get_last_completed_task(self, task_sequence):
        """Find last completed task from sequence"""
        for task_name in reversed(task_sequence):
            if self.checkpoint_exists(task_name):
                return task_name
        return None
    
    def clear_checkpoints(self):
        """Clear all in-memory checkpoints"""
        self.checkpoints.clear()
        print("🗑️ All checkpoints cleared from memory")
    
    def get_all_checkpoints(self):
        """Return all checkpoints for UI display"""
        return self.checkpoints
