import React from 'react';
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
} from '@mui/material';

const GameDetails = ({ game, open, onClose }) => {
  if (!game) return null;

  const renderList = (items, label) => {
    if (!items || items.length === 0) return null;
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          {label}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {items.map((item) => (
            <Chip
              key={item.boardgamemechanic_id || item.boardgamecategory_id || item.boardgamedesigner_id || item.boardgameartist_id || item.boardgamepublisher_id}
              label={item.boardgamemechanic_name || item.boardgamecategory_name || item.boardgamedesigner_name || item.boardgameartist_name || item.boardgamepublisher_name}
              size="small"
            />
          ))}
        </Box>
      </Box>
    );
  };

  const rankCategories = [
    { value: 'rank', label: 'Overall Rank' },
    { value: 'abstracts_rank', label: 'Abstract Games' },
    { value: 'cgs_rank', label: 'Customizable Games' },
    { value: 'childrens_games_rank', label: "Children's Games" },
    { value: 'family_games_rank', label: 'Family Games' },
    { value: 'party_games_rank', label: 'Party Games' },
    { value: 'strategy_games_rank', label: 'Strategy Games' },
    { value: 'thematic_rank', label: 'Thematic Games' },
    { value: 'wargames_rank', label: 'Wargames' }
  ];

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
            <Typography variant="subtitle1" color="text.secondary">
              Published: {game.year_published || 'Unknown'}
            </Typography>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Game Details
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2">
                Players: {game.min_players}-{game.max_players}
              </Typography>
              <Typography variant="body2">
                Playing Time: {game.playing_time} minutes
              </Typography>
              <Typography variant="body2">
                Min Age: {game.min_age}+
              </Typography>
            </Box>
            <Divider sx={{ my: 2 }} />
            {renderList(game.designers, 'Designers')}
            {renderList(game.artists, 'Artists')}
            {renderList(game.mechanics, 'Mechanics')}
            {renderList(game.categories, 'Categories')}
            {renderList(game.publishers, 'Publishers')}
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Statistics
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2">
                Average Rating: {game.average?.toFixed(2) || 'N/A'}
              </Typography>
              <Typography variant="body2">
                Number of Ratings: {game.num_ratings?.toLocaleString() || 'N/A'}
              </Typography>
              <Typography variant="body2">
                Average Weight: {game.average_weight?.toFixed(2) || 'N/A'}
              </Typography>
              <Typography variant="body2">
                Number of Comments: {game.num_comments?.toLocaleString() || 'N/A'}
              </Typography>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              Rankings
            </Typography>
            <Paper sx={{ p: 2 }}>
              <Grid container spacing={1}>
                {rankCategories.map((category) => (
                  <Grid item xs={12} sm={6} key={category.value}>
                    <Typography variant="body2">
                      {category.label}: {game[category.value] || 'Unranked'}
                    </Typography>
                  </Grid>
                ))}
              </Grid>
            </Paper>
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