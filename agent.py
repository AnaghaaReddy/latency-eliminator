"""
LATENCY_ELIMINATOR - Main Agent
Orchestrates the agentic loop:
1. Run script → detect errors
2. Ask Claude to fix
3. Show user, ask for approval
4. Store fix in memory
5. Learn for next script
"""

import sys
import os
from pathlib import Path

# Import our modules
from api_client import ClaudeAPIClient
from script_executor import ScriptExecutor
from memory_simple import MemoryStoreSimple
from memory_redis import MemoryStoreRedis, REDIS_AVAILABLE, MemoryStoreFallback

class LatencyEliminatorAgent:
    def __init__(self, use_redis=False):
        """
        Initialize the agent
        
        Args:
            use_redis (bool): Use Redis backend instead of JSON
        """
        
        print("🚀 Initializing LATENCY_ELIMINATOR Agent...\n")
        
        # Initialize components
        self.api_client = ClaudeAPIClient()
        self.executor = ScriptExecutor(timeout=5)
        
        # Choose memory backend
        if use_redis:
            try:
                self.memory = MemoryStoreRedis()
                print("📦 Using Redis memory backend\n")
            except:
                print("⚠ Redis unavailable, falling back to JSON\n")
                self.memory = MemoryStoreSimple()
        else:
            self.memory = MemoryStoreSimple()
            print("📦 Using JSON memory backend\n")
        
        self.max_iterations = 3
    
    def run_agent(self, script_path):
        """
        Main agentic loop
        
        Args:
            script_path (str): Path to the broken Python script
        
        Returns:
            str: The fixed script content
        """
        
        # Read the script
        try:
            with open(script_path, 'r') as f:
                script_content = f.read()
        except FileNotFoundError:
            print(f"✗ Script not found: {script_path}")
            return None
        
        print(f"📄 Script loaded: {script_path}\n")
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"ITERATION {iteration}/{self.max_iterations}")
            print(f"{'='*60}\n")
            
            # Step 1: Run the script
            print("🏃 Running script...")
            result = self.executor.run(script_path)
            
            if result["success"]:
                print("✓ Script executed successfully!\n")
                return script_content
            
            # Step 2: Error detected
            error_output = result["stderr"]
            print(f"✗ Error detected:\n{error_output}\n")
            
            # Extract error type
            error_type = error_output.split('\n')[-2].split(':')[0] if ':' in error_output else "Error"
            
            # Step 3: Retrieve similar past fixes
            print("🔍 Searching for similar past fixes...")
            similar_fixes = self.memory.retrieve_similar(error_output)
            
            if similar_fixes:
                print(f"✓ Found {len(similar_fixes)} similar fix(es)\n")
                for i, fix in enumerate(similar_fixes, 1):
                    print(f"   Past fix #{i}: {fix['error_type']}")
                    print(f"   Solution: {fix['solution']}\n")
            else:
                print("   (No similar fixes found yet)\n")
            
            # Step 4: Ask Claude to fix
            print("🤖 Asking Claude AI to fix the script...")
            try:
                fixed_code = self.api_client.fix_script(
                    script_content,
                    error_output,
                    past_fixes=similar_fixes
                )
                print("✓ Claude generated a fix\n")
            except Exception as e:
                print(f"✗ Claude API error: {e}")
                return None
            
            # Step 5: Show user the proposed fix
            print("📝 PROPOSED FIX:")
            print("-" * 60)
            print(fixed_code)
            print("-" * 60)
            
            # Step 6: Ask for approval
            print("\n👤 User approval needed:")
            print("   (a) Approve fix and continue")
            print("   (m) Manually edit and continue")
            print("   (r) Reject and stop")
            
            choice = input("\nYour choice (a/m/r): ").strip().lower()
            
            if choice == 'a':
                # Approved: apply the fix
                script_content = fixed_code
                with open(script_path, 'w') as f:
                    f.write(fixed_code)
                print("✓ Fix applied\n")
                
                # Step 7: Store the fix
                self.memory.store_fix(
                    error_type=error_type,
                    error_message=error_output,
                    solution=f"Check similar past fixes and ask Claude to fix",
                    fixed_code=fixed_code
                )
            
            elif choice == 'm':
                # Manual edit
                print("\nEdit the script in your editor and save it.")
                print("Press Enter when done...")
                input()
                
                # Reload the script
                try:
                    with open(script_path, 'r') as f:
                        script_content = f.read()
                    print("✓ Script reloaded\n")
                except:
                    print("✗ Could not reload script\n")
                    return None
            
            elif choice == 'r':
                print("✗ Fix rejected. Stopping.\n")
                return None
            
            else:
                print("✗ Invalid choice. Please try again.\n")
                iteration -= 1  # Don't count invalid choice
        
        print(f"\n✗ Max iterations ({self.max_iterations}) reached")
        return None
    
    def show_stats(self):
        """Display statistics about stored fixes"""
        stats = self.memory.get_stats()
        
        print("\n" + "="*60)
        print("MEMORY STATISTICS")
        print("="*60)
        print(f"Total fixes stored: {stats['total_fixes']}")
        print(f"Error types: {stats.get('error_types', {})}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python agent.py <script_path> [--redis]")
        print("\nExample:")
        print("  python agent.py broken_script.py")
        print("  python agent.py broken_script.py --redis  (use Redis backend)")
        sys.exit(1)
    
    script_path = sys.argv[1]
    use_redis = "--redis" in sys.argv
    
    # Create and run agent
    agent = LatencyEliminatorAgent(use_redis=use_redis)
    fixed_script = agent.run_agent(script_path)
    
    # Show results
    if fixed_script:
        print("\n" + "="*60)
        print("SUCCESS! 🎉")
        print("="*60)
        print(f"Fixed script: {script_path}")
        print("\nFinal code:")
        print("-" * 60)
        print(fixed_script)
        print("-" * 60)
        
        # Show stats
        agent.show_stats()
    else:
        print("\n✗ Failed to fix the script")
        sys.exit(1)


if __name__ == "__main__":
    main()
