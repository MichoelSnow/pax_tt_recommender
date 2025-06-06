import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Chip,
  Divider,
  Card,
  CardContent,
  CardMedia,
  Button,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function GameDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [game, setGame] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGameDetails();
    fetchRecommendations();
  }, [id]);

  const fetchGameDetails = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/games/${id}`);
      setGame(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching game details:', error);
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/games/${id}/recommendations`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  if (loading) {
    return (
      <Container>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  if (!game) {
    return (
      <Container>
        <Typography>Game not found</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/')}
        sx={{ mb: 2 }}
      >
        Back to Games
      </Button>

      <Grid container spacing={3}>
        {/* Game Details */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <img
                  src={game.image_url || '/placeholder.jpg'}
                  alt={game.name}
                  style={{ width: '100%', borderRadius: '8px' }}
                />
              </Grid>
              <Grid item xs={12} md={8}>
                <Typography variant="h4" gutterBottom>
                  {game.name}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  Designed by {game.designer}
                </Typography>
                <Box sx={{ my: 2 }}>
                  <Typography variant="body1">
                    Players: {game.player_count}
                  </Typography>
                  <Typography variant="body1">
                    Play Time: {game.play_time}
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Mechanics
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {game.mechanics.map((mechanic) => (
                    <Chip key={mechanic} label={mechanic} />
                  ))}
                </Box>
                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                  Genres
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {game.genres.map((genre) => (
                    <Chip key={genre} label={genre} />
                  ))}
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12} md={4}>
          <Typography variant="h5" gutterBottom>
            Recommended Games
          </Typography>
          <Grid container spacing={2}>
            {recommendations.map((rec) => (
              <Grid item xs={12} key={rec.id}>
                <Card
                  sx={{
                    display: 'flex',
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'scale(1.02)',
                      transition: 'transform 0.2s ease-in-out',
                    },
                  }}
                  onClick={() => navigate(`/game/${rec.id}`)}
                >
                  <CardMedia
                    component="img"
                    sx={{ width: 100 }}
                    image={rec.image_url || '/placeholder.jpg'}
                    alt={rec.name}
                  />
                  <CardContent>
                    <Typography variant="subtitle1" noWrap>
                      {rec.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {rec.designer}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
}

export default GameDetail; 