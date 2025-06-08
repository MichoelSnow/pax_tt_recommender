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
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default GameDetails; 