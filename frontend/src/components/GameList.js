import React, { useState, useCallback, useEffect } from 'react';
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
  CircularProgress,
  IconButton,
  Chip,
  Skeleton,
  Pagination,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
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
  return textarea.value
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/&#10;/g, '\n')
    .replace(/&#13;/g, '\n')
    .replace(/&nbsp;/g, ' ');
};

// Sort options for the game list
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

// Helper function to get rank label
const getRankLabel = (sortValue) => {
  const option = sortOptions.find(opt => opt.value === sortValue);
  return option ? option.label : 'Rank';
};

// Generate player count options (1-12)
const playerCountOptions = Array.from({ length: 12 }, (_, i) => i + 1);

// Loading skeleton for game cards
const GameCardSkeleton = () => (
  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <Skeleton variant="rectangular" height={140} />
    <CardContent sx={{ flexGrow: 1, p: 1.5 }}>
      <Skeleton variant="text" width="80%" height={24} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width="60%" height={20} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width="40%" height={20} />
    </CardContent>
  </Card>
);

const GameList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
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
  const [selectedMechanics, setSelectedMechanics] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [sortBy, setSortBy] = useState('rank');
  const [designerId, setDesignerId] = useState(null);
  const [artistId, setArtistId] = useState(null);
  const gamesPerPage = 24;

  // Get current page from URL or default to 1
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  // Fetch mechanics
  const { data: mechanics = [] } = useQuery({
    queryKey: ['mechanics'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/mechanics');
      return response.data;
    },
    staleTime: 24 * 60 * 60 * 1000, // 24 hours
  });

  // Fetch games with filters
  const { data: games = [], isLoading, error, isFetching } = useQuery({
    queryKey: ['games', searchTerm, playerCount, recommendations, selectedMechanics, weight, sortBy, designerId, artistId, currentPage],
    queryFn: async () => {
      const params = {
        limit: gamesPerPage,
        skip: (currentPage - 1) * gamesPerPage,
        sort_by: sortBy
      };

      if (searchTerm) params.search = searchTerm;
      if (playerCount) params.players = playerCount;
      if (designerId) params.designer_id = designerId;
      if (artistId) params.artist_id = artistId;

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
      return response.data;
    },
    keepPreviousData: true,
  });

  // Update URL when page changes
  const handlePageChange = (event, newPage) => {
    setSearchParams(prev => {
      prev.set('page', newPage.toString());
      return prev;
    });
  };

  // Reset page when filters change
  useEffect(() => {
    setSearchParams(prev => {
      prev.set('page', '1');
      return prev;
    });
  }, [searchTerm, playerCount, recommendations, selectedMechanics, weight, sortBy, designerId, artistId]);

  const handleGameClick = async (game) => {
    try {
      const response = await axios.get(`http://localhost:8000/games/${game.id}`);
      setSelectedGame(response.data);
      setDetailsOpen(true);
    } catch (err) {
      console.error('Failed to fetch game details:', err);
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

  const renderGameGrid = () => {
    if (isLoading) {
      return (
        <Grid container spacing={2}>
          {Array.from(new Array(12)).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
              <GameCardSkeleton />
            </Grid>
          ))}
        </Grid>
      );
    }

    if (error) {
      return (
        <Alert severity="error">Failed to load games. Please try again later.</Alert>
      );
    }

    return (
      <>
        <Grid container spacing={2}>
          {games.map((game) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={game.id}>
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
                onClick={() => handleGameClick(game)}
              >
                <CardMedia
                  component="img"
                  sx={{ 
                    height: 140,
                    objectFit: 'contain',
                    backgroundColor: '#f5f5f5'
                  }}
                  image={game.image || '/placeholder.png'}
                  alt={game.name}
                />
                <CardContent sx={{ flexGrow: 1, p: 1.5 }}>
                  <Typography variant="h6" sx={{ fontSize: '1rem', mb: 0.5 }}>
                    {game.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {getRankLabel(sortBy)}: {game[sortBy] || 'Unranked'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Published: {game.year_published || 'Unknown'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        {games.length >= gamesPerPage && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <Pagination
              count={10} // Assuming max 10 pages for now
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
              size="large"
              disabled={isFetching}
            />
          </Box>
        )}
      </>
    );
  };

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
          {renderGameGrid()}
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
                    onChange={(e) => setRecommendations(prev => ({ ...prev, best: e.target.checked }))}
                    name="best"
                  />
                }
                label="Best"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={recommendations.recommended}
                    onChange={(e) => setRecommendations(prev => ({ ...prev, recommended: e.target.checked }))}
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
                    onChange={(e) => setWeight(prev => ({ ...prev, beginner: e.target.checked }))}
                    name="beginner"
                  />
                }
                label="Beginner Friendly (≤ 2.0)"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={weight.midweight}
                    onChange={(e) => setWeight(prev => ({ ...prev, midweight: e.target.checked }))}
                    name="midweight"
                  />
                }
                label="Midweight (2.0 - 4.0)"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={weight.heavy}
                    onChange={(e) => setWeight(prev => ({ ...prev, heavy: e.target.checked }))}
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