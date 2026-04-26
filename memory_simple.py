"""
Simple Memory Storage (JSON-based)
For learning: stores fixes in a JSON file
Fast to understand, no external dependencies
"""

import json
import os
from datetime import datetime

class MemoryStoreSimple:
    def __init__(self, storage_file="reference_fixes.json"):
        """
        Initialize simple JSON-based memory store
        
        Args:
            storage_file (str): Path to JSON file for storing fixes
        """
        self.storage_file = storage_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create empty JSON file if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def store_fix(self, error_type, error_message, solution, fixed_code):
        """
        Store a fix in the JSON file
        
        Args:
            error_type (str): Type of error (e.g., "KeyError")
            error_message (str): Full error message
            solution (str): Explanation of the fix
            fixed_code (str): The corrected Python code
        """
        
        # Read existing fixes
        fixes = self._read_fixes()
        
        # Create new fix entry
        new_fix = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "solution": solution,
            "fixed_code": fixed_code
        }
        
        # Add to list
        fixes.append(new_fix)
        
        # Write back to file
        with open(self.storage_file, 'w') as f:
            json.dump(fixes, f, indent=2)
        
        print(f"✓ Stored fix for {error_type}")
    
    def retrieve_similar(self, error_message, max_results=3):
        """
        Find similar past fixes based on error message
        
        Args:
            error_message (str): Current error message
            max_results (int): Max number of similar fixes to return
        
        Returns:
            list: List of similar fixes
        """
        
        fixes = self._read_fixes()
        similar = []
        
        # Simple matching: look for error type in message
        for fix in fixes:
            # Check if error type appears in current error
            if fix["error_type"].lower() in error_message.lower():
                similar.append(fix)
        
        # Return top N results
        return similar[:max_results]
    
    def _read_fixes(self):
        """Read all fixes from JSON file"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_all_fixes(self):
        """Get all stored fixes"""
        return self._read_fixes()
    
    def clear_all(self):
        """Clear all stored fixes (use with caution!)"""
        with open(self.storage_file, 'w') as f:
            json.dump([], f, indent=2)
        print("✓ Cleared all stored fixes")
    
    def get_stats(self):
        """Get statistics about stored fixes"""
        fixes = self._read_fixes()
        
        # Count by error type
        error_counts = {}
        for fix in fixes:
            error_type = fix["error_type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_fixes": len(fixes),
            "error_types": error_counts,
            "most_common": max(error_counts, key=error_counts.get) if error_counts else None
        }


if __name__ == "__main__":
    # Test the memory store
    memory = MemoryStoreSimple()
    
    # Store a test fix
    memory.store_fix(
        error_type="NameError",
        error_message="name 'x' is not defined",
        solution="Define variable before using",
        fixed_code="x = 10\nprint(x)"
    )
    
    # Retrieve similar
    similar = memory.retrieve_similar("NameError: undefined")
    print(f"Found {len(similar)} similar fixes")
    
    # Get stats
    stats = memory.get_stats()
    print(f"Stats: {stats}")
