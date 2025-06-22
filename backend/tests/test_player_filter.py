"""
Player Filter Test Script

This script specifically tests the player count filter to ensure it's using
min_players and max_players correctly.
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

def test_player_filter():
    """Test that the player count filter works correctly."""
    db = SessionLocal()
    
    try:
        print("Testing player count filter...")
        
        # Test 1: Games that support 4 players
        print("1. Testing games that support 4 players...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=5, sort_by="rank", players=4)
        end_time = time.time()
        print(f"   ✅ Found {len(games)} games supporting 4 players in {(end_time - start_time)*1000:.1f}ms")
        
        # Verify the filter worked correctly
        for game in games:
            if game.min_players is not None and game.max_players is not None:
                if not (game.min_players <= 4 <= game.max_players):
                    print(f"   ❌ ERROR: Game '{game.name}' has min_players={game.min_players}, max_players={game.max_players} but should support 4 players")
                    return False
            print(f"      - {game.name}: {game.min_players}-{game.max_players} players")
        
        # Test 2: Games that support 2 players
        print("\n2. Testing games that support 2 players...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=5, sort_by="rank", players=2)
        end_time = time.time()
        print(f"   ✅ Found {len(games)} games supporting 2 players in {(end_time - start_time)*1000:.1f}ms")
        
        # Verify the filter worked correctly
        for game in games:
            if game.min_players is not None and game.max_players is not None:
                if not (game.min_players <= 2 <= game.max_players):
                    print(f"   ❌ ERROR: Game '{game.name}' has min_players={game.min_players}, max_players={game.max_players} but should support 2 players")
                    return False
            print(f"      - {game.name}: {game.min_players}-{game.max_players} players")
        
        # Test 3: Games that support 6 players
        print("\n3. Testing games that support 6 players...")
        start_time = time.time()
        games, total = crud.get_games(db, skip=0, limit=5, sort_by="rank", players=6)
        end_time = time.time()
        print(f"   ✅ Found {len(games)} games supporting 6 players in {(end_time - start_time)*1000:.1f}ms")
        
        # Verify the filter worked correctly
        for game in games:
            if game.min_players is not None and game.max_players is not None:
                if not (game.min_players <= 6 <= game.max_players):
                    print(f"   ❌ ERROR: Game '{game.name}' has min_players={game.min_players}, max_players={game.max_players} but should support 6 players")
                    return False
            print(f"      - {game.name}: {game.min_players}-{game.max_players} players")
        
        print("\n🎉 All player filter tests passed! The filter is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_player_filter() 