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
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Autocomplete,
  CardMedia,
  Pagination,
  CircularProgress,
  InputAdornment,
  IconButton,
  Chip,
  Stack,
  Tooltip,
} from '@mui/material';
import axios from 'axios';
import debounce from 'lodash/debounce';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import CloseIcon from '@mui/icons-material/Close';
import GameDetails from './GameDetails';

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

const GameList = () => {
  const [games, setGames] = useState([]);
  const [filteredGames, setFilteredGames] = useState([]);
  const [displayedGames, setDisplayedGames] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [playerCount, setPlayerCount] = useState('');
  const [recommendations, setRecommendations] = useState({
    best: false,
    recommended: false
  });
  const [weight, setWeight] = useState({
    beginner: false,
    midweight: false,
    heavy: false
  });
  const [mechanics, setMechanics] = useState([]);
  const [selectedMechanics, setSelectedMechanics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [selectedGame, setSelectedGame] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [sortBy, setSortBy] = useState('rank');
  const [designerId, setDesignerId] = useState(null);
  const [artistId, setArtistId] = useState(null);
  const gamesPerPage = 10;

  const sortOptions = [
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

  const getRankLabel = (sortValue) => {
    const option = sortOptions.find(opt => opt.value === sortValue);
    return option ? option.label : 'Rank';
  };

  // Generate player count options (1-12)
  const playerCountOptions = Array.from({ length: 12 }, (_, i) => i + 1);

  useEffect(() => {
    const fetchMechanics = async () => {
      try {
        const response = await axios.get('http://localhost:8000/mechanics');
        setMechanics(response.data);
      } catch (err) {
        console.error('Failed to fetch mechanics:', err);
      }
    };
    fetchMechanics();
  }, []);

  const searchGames = async (term, players, recs, mechs, weightFilter, sort, designer, artist) => {
    try {
      setLoading(true);
      const params = {
        limit: gamesPerPage,
        skip: 0,
        sort_by: sort
      };

      if (term) {
        params.search = term;
      }

      if (players) {
        params.players = players;
      }

      if (designer) {
        params.designer_id = designer;
      }

      if (artist) {
        params.artist_id = artist;
      }

      const activeRecommendations = Object.entries(recs)
        .filter(([_, checked]) => checked)
        .map(([key]) => key);
      
      if (activeRecommendations.length > 0) {
        params.recommendations = activeRecommendations.join(',');
      }

      const activeWeights = Object.entries(weightFilter)
        .filter(([_, checked]) => checked)
        .map(([key]) => key);
      
      if (activeWeights.length > 0) {
        params.weight = activeWeights.join(',');
      }

      if (mechs.length > 0) {
        params.mechanics = mechs.map(m => m.name).join(',');
      }

      console.log('Search params:', params);  // Debug log
      const response = await axios.get('http://localhost:8000/games', { params });
      setGames(response.data);
      setFilteredGames(response.data);
      setDisplayedGames(response.data);
      setPage(1);
      setLoading(false);
    } catch (err) {
      console.error('Search error:', err);
      if (err.response) {
        console.error('Error response:', err.response.data);
        setError(`Error: ${err.response.data.detail || 'Failed to search games. Please try again later.'}`);
      } else if (err.request) {
        console.error('No response received:', err.request);
        setError('No response from server. Please check if the backend is running.');
      } else {
        console.error('Error setting up request:', err.message);
        setError('Failed to search games. Please try again later.');
      }
      setLoading(false);
    }
  };

  // Create a debounced version of the search function
  const debouncedSearch = useCallback(
    debounce((term, players, recs, mechs, weightFilter, sort, designer, artist) => {
      searchGames(term, players, recs, mechs, weightFilter, sort, designer, artist);
    }, 500),
    []
  );

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const params = {
          skip: 0,
          limit: gamesPerPage,
          sort_by: sortBy
        };

        if (playerCount) {
          params.players = playerCount;
        }

        const activeRecommendations = Object.entries(recommendations)
          .filter(([_, checked]) => checked)
          .map(([key]) => key);
        
        if (activeRecommendations.length > 0) {
          params.recommendations = activeRecommendations.join(',');
        }

        const activeWeights = Object.entries(weight)
          .filter(([_, checked]) => checked)
          .map(([key]) => key);
        
        if (activeWeights.length > 0) {
          params.weight = activeWeights.join(',');
        }

        if (selectedMechanics.length > 0) {
          params.mechanics = selectedMechanics.map(m => m.name).join(',');
        }

        const response = await axios.get('http://localhost:8000/games', { params });
        setGames(response.data);
        setFilteredGames(response.data);
        setDisplayedGames(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Fetch error:', err);
        setError('Failed to fetch games. Please try again later.');
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  // Update search when any filter changes
  useEffect(() => {
    debouncedSearch(searchTerm, playerCount, recommendations, selectedMechanics, weight, sortBy, designerId, artistId);
    // Cleanup function to cancel any pending debounced calls
    return () => {
      debouncedSearch.cancel();
    };
  }, [searchTerm, playerCount, recommendations, selectedMechanics, weight, sortBy, designerId, artistId, debouncedSearch]);

  const loadMore = async () => {
    try {
      const nextPage = page + 1;
      const params = {
        skip: (nextPage - 1) * gamesPerPage,
        limit: gamesPerPage,
        search: searchTerm || undefined
      };

      if (playerCount) {
        params.players = playerCount;
      }

      const activeRecommendations = Object.entries(recommendations)
        .filter(([_, checked]) => checked)
        .map(([key]) => key);
      
      if (activeRecommendations.length > 0) {
        params.recommendations = activeRecommendations.join(',');
      }

      if (selectedMechanics.length > 0) {
        params.mechanics = selectedMechanics.map(m => m.name).join(',');
      }

      const response = await axios.get('http://localhost:8000/games', { params });
      
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

  const handleRecommendationChange = (event) => {
    setRecommendations({
      ...recommendations,
      [event.target.name]: event.target.checked
    });
  };

  const handleWeightChange = (event) => {
    setWeight({
      ...weight,
      [event.target.name]: event.target.checked
    });
  };

  const handleGameClick = async (game) => {
    try {
      const response = await axios.get(`http://localhost:8000/games/${game.id}`);
      setSelectedGame(response.data);
      setDetailsOpen(true);
    } catch (err) {
      setError('Failed to fetch game details. Please try again later.');
    }
  };

  const handleFilter = (type, id) => {
    if (type === 'designer') {
      setDesignerId(id);
      setArtistId(null);
      setSearchTerm('');
    } else if (type === 'artist') {
      setArtistId(id);
      setDesignerId(null);
      setSearchTerm('');
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
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ my: 4, display: 'flex', gap: 4 }}>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
            <TextField
              fullWidth
              label="Search games"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Sort By Rank</InputLabel>
              <Select
                value={sortBy}
                label="Sort By Rank"
                onChange={(e) => setSortBy(e.target.value)}
              >
                {sortOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {games.map((game) => (
              <Card 
                key={game.id}
                sx={{ 
                  display: 'flex',
                  cursor: 'pointer',
                  '&:hover': {
                    boxShadow: 6
                  }
                }}
                onClick={() => handleGameClick(game)}
              >
                <CardMedia
                  component="img"
                  sx={{ 
                    width: 150,
                    objectFit: 'contain',
                    backgroundColor: '#f5f5f5'
                  }}
                  image={game.image || '/placeholder.png'}
                  alt={game.name}
                />
                <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {game.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {getRankLabel(sortBy)}: {game[sortBy] || 'Unranked'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Published: {game.year_published || 'Unknown'}
                    </Typography>
                    {game.description && (
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'pre-line'
                        }}
                      >
                        {decodeHtmlEntities(game.description)}
                      </Typography>
                    )}
                  </Box>
                </CardContent>
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
        <Box sx={{ width: 300 }}>
          <FormControl fullWidth sx={{ mb: 2 }}>
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
          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              BGG Player Count Recs
            </Typography>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={recommendations.best}
                    onChange={handleRecommendationChange}
                    name="best"
                  />
                }
                label="Best"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={recommendations.recommended}
                    onChange={handleRecommendationChange}
                    name="recommended"
                  />
                }
                label="Recommended"
              />
            </FormGroup>
          </FormControl>
          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Game Weight
            </Typography>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={weight.beginner}
                    onChange={handleWeightChange}
                    name="beginner"
                  />
                }
                label="Beginner Friendly (≤ 2.0)"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={weight.midweight}
                    onChange={handleWeightChange}
                    name="midweight"
                  />
                }
                label="Midweight (2.0 - 4.0)"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={weight.heavy}
                    onChange={handleWeightChange}
                    name="heavy"
                  />
                }
                label="Heavy Cardboard (≥ 4.0)"
              />
            </FormGroup>
          </FormControl>
          <Divider sx={{ my: 2 }} />
          <FormControl fullWidth>
            <Typography variant="subtitle1" gutterBottom>
              Mechanics
            </Typography>
            <Autocomplete
              multiple
              options={mechanics}
              getOptionLabel={(option) => `${option.name} (${option.count})`}
              value={selectedMechanics}
              onChange={(event, newValue) => {
                setSelectedMechanics(newValue);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  placeholder="Select mechanics"
                />
              )}
              renderOption={(props, option) => {
                const { key, ...otherProps } = props;
                return (
                  <li key={option.name} {...otherProps}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <Typography>{option.name}</Typography>
                      <Typography color="text.secondary">({option.count})</Typography>
                    </Box>
                  </li>
                );
              }}
            />
          </FormControl>
        </Box>
      </Box>
      <GameDetails
        game={selectedGame}
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        onFilter={handleFilter}
      />
    </Container>
  );
};

export default GameList; 