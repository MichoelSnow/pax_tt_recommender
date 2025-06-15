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
  Card,
  CardMedia,
  CardContent,
} from '@mui/material';
import axios from 'axios';
import PeopleIcon from '@mui/icons-material/People';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PsychologyAltOutlinedIcon from '@mui/icons-material/PsychologyAltOutlined';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarBorderOutlinedIcon from '@mui/icons-material/StarBorderOutlined';

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
      <Grid container spacing={2}>
        {recommendations.map((rec) => (
          <Grid item xs={12} sm={6} md={4} key={rec.id}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
                '&:hover': {
                  boxShadow: 6
                }
              }}
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
            >
              <CardMedia
                component="img"
                sx={{ 
                  height: 140,
                  objectFit: 'contain',
                  backgroundColor: '#f5f5f5'
                }}
                image={rec.image || '/placeholder.png'}
                alt={rec.name}
                loading="lazy"
              />
              <CardContent sx={{ flexGrow: 1, p: 1.5 }}>
                <Typography variant="h6" sx={{ fontSize: '1rem', mb: 0.5 }}>
                  {rec.name.length > 100 ? `${rec.name.substring(0, 100)}...` : rec.name}
                </Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: '0.7fr auto', gap: 0.5 }}>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <PeopleIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {rec.min_players === rec.max_players ? rec.min_players : `${rec.min_players}-${rec.max_players}`}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <AccessTimeIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {rec.min_playtime === rec.max_playtime ? `${rec.min_playtime} min` : `${rec.min_playtime}-${rec.max_playtime} min`}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <PsychologyAltOutlinedIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {rec.average_weight ? `${rec.average_weight.toFixed(1)}/5` : 'N/A'}
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                      <EmojiEventsIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {rec.rank || 'Unranked'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <StarBorderOutlinedIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {rec.average ? rec.average.toFixed(1) : 'N/A'}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
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