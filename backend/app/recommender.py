import logging
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from . import models
import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize
import json

logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None
    _game_embeddings = None
    _model_path = None
    _game_mapping = {}  # Maps game IDs to indices
    _reverse_game_mapping = {}  # Maps indices back to game IDs

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self):
        """Load the most recent game embeddings from the data directory."""
        if self._game_embeddings is not None:
            return self._game_embeddings

        # Find the most recent embeddings file
        data_dir = Path(__file__).parent.parent.parent / "data" / "crawler"
        game_embeddings_files = list(data_dir.glob("game_embeddings_*.npz"))
        reverse_mappings_files = list(data_dir.glob("reverse_mappings_*.json"))
        if not game_embeddings_files:
            raise FileNotFoundError("No embeddings files found")

        latest_game_embeddings = max(game_embeddings_files, key=lambda x: x.stat().st_mtime)
        latest_reverse_mappings = max(reverse_mappings_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Loading embeddings from: {latest_game_embeddings}")

        # Load the embeddings
        self._game_embeddings = sparse.load_npz(latest_game_embeddings)
        self._model_path = latest_game_embeddings

        # Load game mappings from the corresponding reverse mappings file
        with open(latest_reverse_mappings, "r") as f:
            self._reverse_game_mapping = {int(k): v for k, v in json.load(f).items()} 
            self._game_mapping = {v: k for k, v in self._reverse_game_mapping.items()}

        return self._game_embeddings

    def get_model(self):
        """Get the current embeddings, loading them if necessary."""
        if self._game_embeddings is None:
            self.load_model()
        return self._game_embeddings

def get_recommendations(
    game_id: int,
    db: Session,
    limit: int = 5,
    disliked_games: Optional[List[int]] = None,
    anti_weight: float = 1.0
) -> List[models.BoardGame]:
    """
    Get game recommendations using the game embeddings.
    
    Args:
        game_id: ID of the game to get recommendations for
        db: Database session
        limit: Maximum number of recommendations to return
        disliked_games: Optional list of game IDs to use as anti-recommendations
        anti_weight: Weight to apply to anti-recommendations
        
    Returns:
        List of recommended BoardGame objects
    """
    try:
        model_manager = ModelManager.get_instance()
        game_embeddings = model_manager.get_model()
        game_mapping = model_manager._game_mapping
        reverse_game_mapping = model_manager._reverse_game_mapping
        
        
        
        if game_id not in game_mapping:
            logger.warning(f"Game ID {game_id} not found in embeddings")
            return []

        # Get embedding for the input game
        # game_idx = game_mapping[game_id]
        # game_vec = game_embeddings[game_idx]


        # Initialize scores array
        # scores = np.zeros(game_embeddings.shape[0])
        
        # Add positive contribution from liked game
        # scores += game_embeddings @ game_vec.T
        
        # # Apply anti-recommendations if provided
        # if disliked_games:
        #     disliked_vec = np.zeros(game_embeddings.shape[1])
        #     for dg_id in disliked_games:
        #         if dg_id in game_mapping:
        #             dg_idx = game_mapping[dg_id]
        #             disliked_vec += game_embeddings[dg_idx].toarray().flatten()
        #     if len(disliked_games) > 0:
        #         disliked_vec /= len(disliked_games)
        #         scores -= anti_weight * (game_embeddings @ disliked_vec)
        
        # # Remove input games from recommendations
        # scores[game_idx] = -1
        # if disliked_games:
        #     for dg_id in disliked_games:
        #         dg_id_str = str(dg_id)
        #         if dg_id_str in game_mapping:
        #             scores[game_mapping[dg_id_str]] = -1


        # Compute query vector
        liked_indices = [game_mapping[game_id]]
        disliked_indices = [game_mapping[dg_id] for dg_id in disliked_games] if disliked_games else []

        # Compute mean of liked and disliked games
        pos_vec = game_embeddings[liked_indices].mean(axis=0)
        neg_vec = game_embeddings[disliked_indices].mean(axis=0) if disliked_indices else 0
        query_vec = pos_vec - anti_weight * neg_vec
        query_vec = normalize(np.asarray(query_vec), norm='l2')

        # Compute cosine similarity between query vector and all game embeddings
        scores = game_embeddings @ query_vec.T
        scores = np.asarray(scores).ravel()

        # Zero out scores for input items
        for idx in liked_indices + (disliked_indices or []):
            scores[idx] = -1
        
        # Get top N similar games
        top_indices = np.argsort(scores)[-limit:][::-1]
        recommended_ids = [
            int(reverse_game_mapping[idx]) 
            for idx in top_indices 
            if scores[idx] > 0
        ]
        
        # Get full game objects from database
        return db.query(models.BoardGame).filter(
            models.BoardGame.id.in_(recommended_ids)
        ).all()
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
        return []
