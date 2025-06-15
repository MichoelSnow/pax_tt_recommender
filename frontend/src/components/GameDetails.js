import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Chip,
  Divider,
  Paper,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

// Helper function to decode HTML entities and preserve line breaks
const decodeHtmlEntities = (text) => {
  if (!text) return '';
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  // Convert HTML line breaks to newlines and preserve them
  return textarea.value
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/&#10;/g, '\n')
    .replace(/&#13;/g, '\n')
    .replace(/&nbsp;/g, ' ');
};

const GameDetails = ({ game, open, onClose, onFilter }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!game) return;
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:8000/recommendations/${game.id}`);
        setRecommendations(response.data);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
      } finally {
        setLoading(false);
      }
    };

    if (open && game) {
      fetchRecommendations();
    }
  }, [game, open]);

  if (!game) return null;

  const renderList = (items, label, type) => {
    if (!items || items.length === 0) return null;
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          {label}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {items.map((item) => {
            const name = item.boardgamemechanic_name || item.boardgamecategory_name || 
                        item.boardgamedesigner_name || item.boardgameartist_name || 
                        item.boardgamepublisher_name;
            const id = item.boardgamemechanic_id || item.boardgamecategory_id || 
                      item.boardgamedesigner_id || item.boardgameartist_id || 
                      item.boardgamepublisher_id;
            const isClickable = type === 'designer' || type === 'artist' || 
                              type === 'mechanic' || type === 'category';
            
            return (
              <Chip
                key={id}
                label={name}
                size="small"
                onClick={isClickable ? () => {
                  onFilter(type, id, name);
                  onClose();
                } : undefined}
                sx={isClickable ? {
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'action.hover'
                  }
                } : undefined}
              />
            );
          })}
        </Box>
      </Box>
    );
  };

  const renderRecommendations = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress />
        </Box>
      );
    }

    if (!recommendations || recommendations.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary">
          No recommendations available.
        </Typography>
      );
    }

    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {recommendations.map((rec) => (
          <Chip
            key={rec.id}
            label={rec.name}
            size="small"
            onClick={() => {
              onClose();
              // Fetch and show the recommended game's details
              axios.get(`http://localhost:8000/games/${rec.id}`)
                .then(response => {
                  onFilter('game', rec.id, rec.name);
                })
                .catch(err => {
                  console.error('Failed to fetch recommended game:', err);
                });
            }}
            sx={{
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: 'action.hover'
              }
            }}
          />
        ))}
      </Box>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      scroll="paper"
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {game.image && (
            <Box
              component="img"
              src={game.image}
              alt={game.name}
              sx={{
                width: 100,
                height: 100,
                objectFit: 'contain',
                backgroundColor: '#f5f5f5'
              }}
            />
          )}
          <Box>
            <Typography variant="h5">{game.name}</Typography>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            {renderList(game.designers, 'Designers', 'designer')}
            {renderList(game.artists, 'Artists', 'artist')}
            {renderList(game.mechanics, 'Mechanics', 'mechanic')}
            {renderList(game.categories, 'Categories', 'category')}
            {renderList(game.publishers, 'Publishers', 'publisher')}
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Description
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                whiteSpace: 'pre-line',
                mb: 2
              }}
            >
              {decodeHtmlEntities(game.description)}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              Similar Games
            </Typography>
            {renderRecommendations()}
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default GameDetails; 