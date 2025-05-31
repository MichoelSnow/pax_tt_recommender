import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple

class GameRecommender:
    def __init__(self, min_ratings_per_user: int = 3):
        """
        Initialize the recommender system.
        
        Args:
            min_ratings_per_user (int): Minimum number of ratings a user must have to be included
        """
        self.min_ratings_per_user = min_ratings_per_user
        self.user_mapping = {}  # Maps user IDs to indices
        self.game_mapping = {}  # Maps game IDs to indices
        self.reverse_game_mapping = {}  # Maps indices back to game IDs
        self.rating_matrix = None
        self.game_similarity = None
        
    def _create_rating_matrix(self, df: pd.DataFrame) -> sparse.csr_matrix:
        """
        Convert the input dataframe into a sparse rating matrix.
        
        Args:
            df (pd.DataFrame): Input dataframe with game_id as index and rating columns containing user lists
            
        Returns:
            sparse.csr_matrix: Sparse matrix of user-game ratings
        """
        # Create mappings for users and games
        all_users = set()
        for col in df.columns:
            all_users.update([user for users in df[col].dropna() for user in users])
        
        # Create user mapping
        for i, user in enumerate(sorted(all_users)):
            self.user_mapping[user] = i
            
        # Create game mapping
        for i, game_id in enumerate(df.index):
            self.game_mapping[game_id] = i
            self.reverse_game_mapping[i] = game_id
            
        # Initialize sparse matrix
        n_users = len(self.user_mapping)
        n_games = len(self.game_mapping)
        rating_matrix = sparse.lil_matrix((n_users, n_games))
        
        # Fill the rating matrix
        for game_id, row in df.iterrows():
            game_idx = self.game_mapping[game_id]
            for rating, users in row.items():
                if isinstance(users, list) and len(users) > 0:  # Check if users is a non-empty list
                    for user in users:
                        if user in self.user_mapping:
                            user_idx = self.user_mapping[user]
                            rating_matrix[user_idx, game_idx] = float(rating)
        
        # Convert to CSR format for efficient operations
        return rating_matrix.tocsr()
    
    def _filter_users(self, rating_matrix: sparse.csr_matrix) -> sparse.csr_matrix:
        """
        Remove users with fewer than min_ratings_per_user ratings.
        
        Args:
            rating_matrix (sparse.csr_matrix): Input rating matrix
            
        Returns:
            sparse.csr_matrix: Filtered rating matrix
        """
        # Count non-zero elements per user (number of ratings)
        user_rating_counts = np.diff(rating_matrix.indptr)
        
        # Get indices of users with enough ratings
        valid_user_indices = np.where(user_rating_counts >= self.min_ratings_per_user)[0]
        
        # Filter the matrix
        return rating_matrix[valid_user_indices]
    
    def fit(self, df: pd.DataFrame) -> None:
        """
        Fit the recommender system to the input data.
        
        Args:
            df (pd.DataFrame): Input dataframe with game_id as index and rating columns containing user lists
        """
        # Create and filter rating matrix
        self.rating_matrix = self._create_rating_matrix(df)
        self.rating_matrix = self._filter_users(self.rating_matrix)
        
        # Compute game similarity matrix
        self.game_similarity = cosine_similarity(self.rating_matrix.T)
        
    def recommend_similar_games(self, 
                              game_ids: List[str], 
                              disliked_games: List[str] = None,
                              n_recommendations: int = 5,
                              anti_weight: float = 1.0) -> List[Tuple[str, float]]:
        """
        Generate recommendations based on a list of game IDs, with optional anti-recommendations.
        
        Args:
            game_ids (List[str]): List of game IDs to base recommendations on
            disliked_games (List[str], optional): List of game IDs to use as anti-recommendations
            n_recommendations (int): Number of recommendations to generate
            anti_weight (float): Weight to apply to anti-recommendations (higher values = stronger anti-recommendations)
            
        Returns:
            List[Tuple[str, float]]: List of (game_id, similarity_score) tuples
        """
        # Convert liked game IDs to indices
        game_indices = []
        for game_id in game_ids:
            if game_id in self.game_mapping:
                game_indices.append(self.game_mapping[game_id])
        
        if not game_indices:
            return []
            
        # Calculate average similarity scores for all games
        avg_similarities = np.zeros(len(self.game_mapping))
        for game_idx in game_indices:
            avg_similarities += self.game_similarity[game_idx]
        avg_similarities /= len(game_indices)
        
        # Apply anti-recommendations if provided
        if disliked_games:
            disliked_indices = []
            for game_id in disliked_games:
                if game_id in self.game_mapping:
                    disliked_indices.append(self.game_mapping[game_id])
            
            if disliked_indices:
                # Calculate average similarity to disliked games
                anti_similarities = np.zeros(len(self.game_mapping))
                for game_idx in disliked_indices:
                    anti_similarities += self.game_similarity[game_idx]
                anti_similarities /= len(disliked_indices)
                
                # Subtract anti-similarities from the main similarities
                avg_similarities -= anti_similarities * anti_weight
        
        # Remove the input games from recommendations
        for game_idx in game_indices:
            avg_similarities[game_idx] = -1
        if disliked_games:
            for game_idx in disliked_indices:
                avg_similarities[game_idx] = -1
            
        # Get top N similar games
        top_indices = np.argsort(avg_similarities)[-n_recommendations:][::-1]
        
        return [(self.reverse_game_mapping[idx], avg_similarities[idx]) 
                for idx in top_indices if avg_similarities[idx] > 0]
