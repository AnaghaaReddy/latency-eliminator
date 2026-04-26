"""
Production Memory Storage (Redis-based)
For production: stores fixes in Redis for speed
Requires Redis server: redis-server
Optional: only use if you want to learn about Redis
"""

import json
import os
from datetime import datetime

# Try to import redis, but don't fail if not installed
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class MemoryStoreRedis:
    def __init__(self, host='localhost', port=6379, db=0):
        """
        Initialize Redis-based memory store
        
        Args:
            host (str): Redis server host
            port (int): Redis server port
            db (int): Redis database number
        """
        
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not installed. Run: pip install redis")
        
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            # Test connection
            self.redis.ping()
            print("✓ Connected to Redis")
        except:
            raise ConnectionError(
                "Could not connect to Redis. Make sure Redis is running:\n"
                "On Windows: Download from https://github.com/microsoftarchive/redis/releases\n"
                "On Mac: brew install redis && redis-server\n"
                "On Linux: sudo apt install redis-server && redis-server"
            )
    
    def store_fix(self, error_type, error_message, solution, fixed_code):
        """
        Store a fix in Redis
        
        Args:
            error_type (str): Type of error (e.g., "KeyError")
            error_message (str): Full error message
            solution (str): Explanation of the fix
            fixed_code (str): The corrected Python code
        """
        
        # Create unique key based on error type and timestamp
        key = f"fix:{error_type}:{int(datetime.now().timestamp())}"
        
        # Store as JSON
        fix_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "solution": solution,
            "fixed_code": fixed_code
        }
        
        # Store in Redis (with 30-day expiration)
        self.redis.setex(key, 30*24*60*60, json.dumps(fix_data))
        
        # Also maintain a list of all fixes by error type
        list_key = f"fixes:{error_type}"
        self.redis.rpush(list_key, key)
        
        print(f"✓ Stored fix for {error_type} in Redis")
    
    def retrieve_similar(self, error_message, max_results=3):
        """
        Find similar past fixes based on error message
        
        Args:
            error_message (str): Current error message
            max_results (int): Max number of similar fixes to return
        
        Returns:
            list: List of similar fixes
        """
        
        # Extract error type from message
        error_type = self._extract_error_type(error_message)
        
        if not error_type:
            return []
        
        # Get list of fixes for this error type
        list_key = f"fixes:{error_type}"
        fix_keys = self.redis.lrange(list_key, 0, max_results-1)
        
        similar = []
        for key in fix_keys:
            try:
                fix_json = self.redis.get(key)
                if fix_json:
                    fix_data = json.loads(fix_json)
                    similar.append(fix_data)
            except:
                pass
        
        return similar
    
    def _extract_error_type(self, error_message):
        """Extract error type from error message"""
        # Simple extraction: take first word before colon
        if ':' in error_message:
            return error_message.split(':')[0].strip()
        return None
    
    def get_all_fixes(self):
        """Get all stored fixes"""
        fixes = []
        
        # Get all fix keys
        for key in self.redis.scan_iter("fix:*"):
            try:
                fix_json = self.redis.get(key)
                if fix_json:
                    fixes.append(json.loads(fix_json))
            except:
                pass
        
        return fixes
    
    def clear_all(self):
        """Clear all stored fixes (use with caution!)"""
        # Delete all fix keys
        for key in self.redis.scan_iter("fix:*"):
            self.redis.delete(key)
        for key in self.redis.scan_iter("fixes:*"):
            self.redis.delete(key)
        print("✓ Cleared all fixes from Redis")
    
    def get_stats(self):
        """Get statistics about stored fixes"""
        stats = {
            "total_fixes": 0,
            "error_types": {}
        }
        
        # Count fixes by error type
        for key in self.redis.scan_iter("fixes:*"):
            error_type = key.replace("fixes:", "")
            count = self.redis.llen(key)
            stats["error_types"][error_type] = count
            stats["total_fixes"] += count
        
        return stats


# Fallback: if Redis not available, use simple memory
class MemoryStoreFallback:
    """Falls back to simple in-memory storage if Redis unavailable"""
    
    def __init__(self):
        self.fixes = []
        print("⚠ Redis not available. Using in-memory storage (data will be lost on restart)")
    
    def store_fix(self, error_type, error_message, solution, fixed_code):
        self.fixes.append({
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "solution": solution,
            "fixed_code": fixed_code
        })
        print(f"✓ Stored fix for {error_type} (in memory)")
    
    def retrieve_similar(self, error_message, max_results=3):
        return [f for f in self.fixes if f["error_type"] in error_message][:max_results]
    
    def get_all_fixes(self):
        return self.fixes
    
    def clear_all(self):
        self.fixes = []


if __name__ == "__main__":
    if REDIS_AVAILABLE:
        try:
            memory = MemoryStoreRedis()
            print("✓ Redis memory store initialized")
        except ConnectionError as e:
            print(f"✗ {e}")
    else:
        print("Redis not installed. Install with: pip install redis")
