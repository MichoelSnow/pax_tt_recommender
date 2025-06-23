import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  Divider,
  Tooltip,
} from '@mui/material';
import CancelIcon from '@mui/icons-material/Cancel';

const LikedGamesDialog = ({
  open,
  onClose,
  likedGames,
  dislikedGames,
  onRemoveLike,
  onRemoveDislike,
}) => {
  const sortedLiked = [...likedGames].sort((a, b) => a.name.localeCompare(b.name));
  const sortedDisliked = [...dislikedGames].sort((a, b) => a.name.localeCompare(b.name));

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Liked and Disliked Games</DialogTitle>
      <DialogContent dividers>
        <Box mb={2}>
          <Typography variant="h6" gutterBottom>
            Liked Games ({sortedLiked.length})
          </Typography>
          {sortedLiked.length > 0 ? (
            <Box display="flex" flexWrap="wrap" gap={1}>
              {sortedLiked.map((game) => (
                <Chip
                  key={game.id}
                  label={game.name}
                  onDelete={() => onRemoveLike(game)}
                  deleteIcon={
                    <Tooltip title="Remove from liked">
                      <CancelIcon />
                    </Tooltip>
                  }
                />
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No liked games yet.
            </Typography>
          )}
        </Box>
        <Divider sx={{ my: 2 }} />
        <Box>
          <Typography variant="h6" gutterBottom>
            Disliked Games ({sortedDisliked.length})
          </Typography>
          {sortedDisliked.length > 0 ? (
            <Box display="flex" flexWrap="wrap" gap={1}>
              {sortedDisliked.map((game) => (
                <Chip
                  key={game.id}
                  label={game.name}
                  onDelete={() => onRemoveDislike(game)}
                  deleteIcon={
                    <Tooltip title="Remove from disliked">
                      <CancelIcon />
                    </Tooltip>
                  }
                  color="error"
                  variant="outlined"
                />
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No disliked games yet.
            </Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default LikedGamesDialog; 