"""
Script Executor
Runs Python scripts and captures output/errors safely
"""

import subprocess
import os

class ScriptExecutor:
    def __init__(self, timeout=5):
        """
        Initialize script executor
        
        Args:
            timeout (int): Max seconds to run a script before killing it
        """
        self.timeout = timeout
    
    def run(self, script_path):
        """
        Execute a Python script and capture output/errors
        
        Args:
            script_path (str): Path to Python script to run
        
        Returns:
            dict: {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "return_code": int
            }
        """
        
        # Check if file exists
        if not os.path.exists(script_path):
            return {
                "success": False,
                "stdout": "",
                "stderr": f"File not found: {script_path}",
                "return_code": -1
            }
        
        try:
            # Run the script
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Script timed out after {self.timeout} seconds",
                "return_code": -1
            }
        
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "return_code": -1
            }
    
    def run_inline(self, script_content):
        """
        Run Python code from a string (not a file)
        
        Args:
            script_content (str): Python code as string
        
        Returns:
            dict: Same as run() method
        """
        
        # Create temporary file
        temp_file = "temp_script.py"
        
        try:
            # Write code to temp file
            with open(temp_file, 'w') as f:
                f.write(script_content)
            
            # Run it
            result = self.run(temp_file)
            
            return result
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    # Test the executor
    executor = ScriptExecutor()
    
    # Create a test script
    test_script = """
print("Hello, World!")
x = 5
print(f"x = {x}")
"""
    
    with open("test_hello.py", "w") as f:
        f.write(test_script)
    
    result = executor.run("test_hello.py")
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout']}")
    
    # Clean up
    os.remove("test_hello.py")
