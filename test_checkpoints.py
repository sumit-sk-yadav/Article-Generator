"""
Test script to verify checkpoint functionality
Run with: python test_checkpoints.py
"""
import os
import time
from dotenv import load_dotenv
from src.crew_manager import CrewManager

load_dotenv()

def test_checkpoint_creation():
    """Test 1: Verify checkpoints are created after each task"""
    print("\n" + "="*60)
    print("TEST 1: Checkpoint Creation")
    print("="*60 + "\n")
    
    manager = CrewManager()
    
    # Start generation
    print("Starting article generation...")
    try:
        result = manager.run_crew(
            topic="Test Topic: Benefits of AI",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            force_restart=True
        )
        
        # Check checkpoints
        checkpoints = manager.get_checkpoints()
        print(f"\n✅ Generation completed!")
        print(f"📊 Checkpoints created: {list(checkpoints.keys())}")
        
        # Verify all three checkpoints exist
        expected = ['plan', 'write', 'edit']
        for task in expected:
            if task in checkpoints:
                print(f"  ✓ {task}: {len(checkpoints[task]['output'])} characters")
            else:
                print(f"  ✗ {task}: MISSING!")
        
        return len(checkpoints) == 3
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        
        # Even on failure, check what was saved
        checkpoints = manager.get_checkpoints()
        if checkpoints:
            print(f"📊 Partial checkpoints saved: {list(checkpoints.keys())}")
        return False


def test_checkpoint_resume():
    """Test 2: Verify checkpoints are used when resuming"""
    print("\n" + "="*60)
    print("TEST 2: Checkpoint Resume")
    print("="*60 + "\n")
    
    manager = CrewManager()
    topic = "Test Topic: Future of Quantum Computing"
    
    # First run - complete generation
    print("Step 1: Complete generation (creating checkpoints)...")
    try:
        result1 = manager.run_crew(
            topic=topic,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            force_restart=True
        )
        
        checkpoints_after_first = manager.get_checkpoints()
        print(f"✅ First run completed. Checkpoints: {list(checkpoints_after_first.keys())}")
        
    except Exception as e:
        print(f"❌ First run failed: {e}")
        return False
    
    # Second run - should use checkpoints
    print("\nStep 2: Re-run same topic (should use checkpoints)...")
    start_time = time.time()
    
    try:
        result2 = manager.run_crew(
            topic=topic,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            force_restart=False  # Don't clear checkpoints
        )
        
        elapsed = time.time() - start_time
        
        print(f"✅ Second run completed in {elapsed:.2f} seconds")
        
        # If checkpoints worked, second run should be instant
        if elapsed < 5:
            print("✓ Checkpoints were used! (Run completed quickly)")
            return True
        else:
            print("⚠️  Checkpoints may not have been used (run took too long)")
            return False
            
    except Exception as e:
        print(f"❌ Second run failed: {e}")
        return False


def test_checkpoint_clear():
    """Test 3: Verify checkpoint clearing works"""
    print("\n" + "="*60)
    print("TEST 3: Checkpoint Clearing")
    print("="*60 + "\n")
    
    manager = CrewManager()
    
    # Create some checkpoints
    print("Creating test checkpoints...")
    manager.checkpoint_manager.save_checkpoint('plan', 'test plan output', 'planner')
    manager.checkpoint_manager.save_checkpoint('write', 'test write output', 'writer')
    
    checkpoints_before = manager.get_checkpoints()
    print(f"Checkpoints before clear: {list(checkpoints_before.keys())}")
    
    # Clear checkpoints
    manager.checkpoint_manager.clear_checkpoints()
    
    checkpoints_after = manager.get_checkpoints()
    print(f"Checkpoints after clear: {list(checkpoints_after.keys())}")
    
    if len(checkpoints_after) == 0:
        print("✅ Checkpoints cleared successfully!")
        return True
    else:
        print("❌ Checkpoints not cleared!")
        return False


def test_partial_checkpoint_recovery():
    """Test 4: Simulate failure and verify partial checkpoints"""
    print("\n" + "="*60)
    print("TEST 4: Partial Checkpoint Recovery")
    print("="*60 + "\n")
    
    manager = CrewManager()
    
    # Manually create partial checkpoints (simulating a failure after plan task)
    print("Simulating failure scenario (plan completed, write/edit failed)...")
    manager.checkpoint_manager.clear_checkpoints()
    manager.checkpoint_manager.save_checkpoint(
        'plan', 
        'Simulated plan output with outline and keywords',
        'planner'
    )
    
    # Check last completed task
    last_completed = manager.checkpoint_manager.get_last_completed_task(['plan', 'write', 'edit'])
    print(f"Last completed task: {last_completed}")
    
    # Verify checkpoint exists
    plan_checkpoint = manager.checkpoint_manager.load_checkpoint('plan')
    
    if last_completed == 'plan' and plan_checkpoint:
        print(f"✅ Partial checkpoint detected correctly!")
        print(f"   Checkpoint content preview: {plan_checkpoint['output'][:50]}...")
        return True
    else:
        print("❌ Partial checkpoint detection failed!")
        return False


def run_all_tests():
    """Run all checkpoint tests"""
    print("\n" + "="*60)
    print("CHECKPOINT SYSTEM TEST SUITE")
    print("="*60)
    
    results = {
        "Checkpoint Creation": test_checkpoint_creation(),
        "Checkpoint Resume": test_checkpoint_resume(),
        "Checkpoint Clearing": test_checkpoint_clear(),
        "Partial Recovery": test_partial_checkpoint_recovery()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())


if __name__ == "__main__":
    # Check if API keys are available
    if not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("❌ Error: API keys not found in .env file")
        print("Please create a .env file with:")
        print("  GROQ_API_KEY=your_key_here")
        print("  TAVILY_API_KEY=your_key_here")
        exit(1)
    
    success = run_all_tests()
    exit(0 if success else 1)
