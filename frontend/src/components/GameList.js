import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Box,
  Alert,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import axios from 'axios';
import debounce from 'lodash/debounce';

const GameList = () => {
  const [games, setGames] = useState([]);
  const [filteredGames, setFilteredGames] = useState([]);
  const [displayedGames, setDisplayedGames] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [playerCount, setPlayerCount] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const gamesPerPage = 10;

  // Generate player count options (1-12)
  const playerCountOptions = Array.from({ length: 12 }, (_, i) => i + 1);

  const searchGames = async (term, players) => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/games/', {
        params: {
          search: term,
          players: players,
          limit: gamesPerPage,
          skip: 0
        }
      });
      setGames(response.data);
      setFilteredGames(response.data);
      setDisplayedGames(response.data);
      setPage(1);
      setLoading(false);
    } catch (err) {
      setError('Failed to search games. Please try again later.');
      setLoading(false);
    }
  };

  // Create a debounced version of the search function
  const debouncedSearch = useCallback(
    debounce((term, players) => {
      searchGames(term, players);
    }, 500),
    []
  );

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await axios.get('http://localhost:8000/games/', {
          params: {
            skip: 0,
            limit: gamesPerPage,
            players: playerCount
          }
        });
        setGames(response.data);
        setFilteredGames(response.data);
        setDisplayedGames(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch games. Please try again later.');
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  // Update search when either search term or player count changes
  useEffect(() => {
    debouncedSearch(searchTerm, playerCount);
    // Cleanup function to cancel any pending debounced calls
    return () => {
      debouncedSearch.cancel();
    };
  }, [searchTerm, playerCount, debouncedSearch]);

  const loadMore = async () => {
    try {
      const nextPage = page + 1;
      const response = await axios.get('http://localhost:8000/games/', {
        params: {
          skip: (nextPage - 1) * gamesPerPage,
          limit: gamesPerPage,
          search: searchTerm,
          players: playerCount
        }
      });
      
      if (response.data.length > 0) {
        const newGames = [...games, ...response.data];
        setGames(newGames);
        setFilteredGames(newGames);
        setDisplayedGames(newGames);
        setPage(nextPage);
      }
    } catch (err) {
      setError('Failed to load more games. Please try again later.');
    }
  };

  if (loading) {
    return (
      <Container>
        <Typography variant="h6">Loading games...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4, display: 'flex', gap: 4 }}>
        <Box sx={{ flex: 1 }}>
          <TextField
            fullWidth
            label="Search games"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ mb: 4 }}
          />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {displayedGames.map((game) => (
              <Card key={game.id}>
                <Box sx={{ display: 'flex', p: 2 }}>
                  {game.image && (
                    <Box
                      component="img"
                      src={game.image}
                      alt={game.name}
                      sx={{
                        width: 100,
                        height: 100,
                        objectFit: 'contain',
                        display: 'block',
                        marginRight: 2,
                        backgroundColor: '#f5f5f5'
                      }}
                    />
                  )}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {game.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Rank: {game.rank || 'Unranked'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Published: {game.year_published || 'Unknown'}
                    </Typography>
                  </Box>
                </Box>
              </Card>
            ))}
          </Box>
          {displayedGames.length >= gamesPerPage && (
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Button 
                variant="contained" 
                onClick={loadMore}
              >
                Load More
              </Button>
            </Box>
          )}
        </Box>
        <Box sx={{ width: 200 }}>
          <FormControl fullWidth>
            <InputLabel>Number of Players</InputLabel>
            <Select
              value={playerCount}
              label="Number of Players"
              onChange={(e) => setPlayerCount(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              {playerCountOptions.map((count) => (
                <MenuItem key={count} value={count}>
                  {count} {count === 1 ? 'Player' : 'Players'}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Box>
    </Container>
  );
};

export default GameList; 