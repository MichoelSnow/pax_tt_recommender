"""
Database Query Test Script

This script tests that the database queries work without hanging.
"""

import sys
from pathlib import Path
from sqlalchemy.orm import Session
import time

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app import crud, models
from app.database import SessionLocal

def test_basic_queries():
    """Test basic database queries to ensure they don't hang."""
    db = SessionLocal()
    
    try:
        print("Testing basic queries...")
        
        # Test 1: Simple games query
        print("1. Testing simple games query...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=10, sort_by="rank")
        end_time = time.time()
        print(f"   ✅ Success: {len(games)} games in {(end_time - start_time)*1000:.1f}ms")
        
        # Test 2: Games with search
        print("2. Testing games with search...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=10, sort_by="rank", search="catan")
        end_time = time.time()
        print(f"   ✅ Success: {len(games)} games in {(end_time - start_time)*1000:.1f}ms")
        
        # Test 3: Games with player filter
        print("3. Testing games with player filter...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=10, sort_by="rank", players=4)
        end_time = time.time()
        print(f"   ✅ Success: {len(games)} games in {(end_time - start_time)*1000:.1f}ms")
        
        # Test 4: Games with weight filter
        print("4. Testing games with weight filter...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=10, sort_by="rank", weight="beginner")
        end_time = time.time()
        print(f"   ✅ Success: {len(games)} games in {(end_time - start_time)*1000:.1f}ms")
        
        # Test 5: Mechanics query
        print("5. Testing mechanics query...")
        start_time = time.time()
        mechanics = crud.get_mechanics_cached(db, skip=0, limit=50)
        end_time = time.time()
        print(f"   ✅ Success: {len(mechanics)} mechanics in {(end_time - start_time)*1000:.1f}ms")
        
        print("\n🎉 All tests passed! Database queries are working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    test_basic_queries() 