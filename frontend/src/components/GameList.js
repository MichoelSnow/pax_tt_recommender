import React, { useState, useCallback, useEffect, memo } from 'react';
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
  useMediaQuery,
  useTheme,
  InputAdornment,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import debounce from 'lodash/debounce';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import CloseIcon from '@mui/icons-material/Close';
import PeopleIcon from '@mui/icons-material/People';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PsychologyAltOutlinedIcon from '@mui/icons-material/PsychologyAltOutlined';
import StarBorderOutlinedIcon from '@mui/icons-material/StarBorderOutlined';
import GameDetails from './GameDetails';
import GameCard from './GameCard';

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

// Memoized GameCardSkeleton component
const GameCardSkeleton = memo(() => (
  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <Skeleton variant="rectangular" height={140} />
    <CardContent sx={{ flexGrow: 1, p: 1.5 }}>
      <Skeleton variant="text" width="80%" height={24} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width="60%" height={20} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width="40%" height={20} />
    </CardContent>
  </Card>
));

const GameList = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [searchParams, setSearchParams] = useSearchParams();
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
  const [selectedDesigners, setSelectedDesigners] = useState([]);
  const [selectedArtists, setSelectedArtists] = useState([]);
  const [selectedMechanics, setSelectedMechanics] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [sortBy, setSortBy] = useState('rank');
  const [currentPage, setCurrentPage] = useState(1);
  const gamesPerPage = 24;

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce((value) => {
      setSearchTerm(value);
    }, 500),
    []
  );

  // Handle search input change
  const handleSearchChange = (event) => {
    debouncedSearch(event.target.value);
  };

  // Remove page parameter from URL on mount
  useEffect(() => {
    if (searchParams.has('page')) {
      searchParams.delete('page');
      setSearchParams(searchParams);
    }
  }, []);

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
  const { data: response = { games: [], total: 0 }, isLoading, error, isFetching } = useQuery({
    queryKey: ['games', searchTerm, playerCount, recommendations, selectedDesigners, selectedArtists, selectedMechanics, selectedCategories, weight, sortBy, currentPage],
    queryFn: async () => {
      const params = {
        limit: gamesPerPage,
        skip: (currentPage - 1) * gamesPerPage,
        sort_by: sortBy
      };

      if (searchTerm) params.search = searchTerm;
      if (playerCount) params.players = playerCount;

      if (selectedDesigners.length > 0) {
        params.designer_id = selectedDesigners.map(d => d.boardgamedesigner_id).join(',');
      }

      if (selectedArtists.length > 0) {
        params.artist_id = selectedArtists.map(a => a.boardgameartist_id).join(',');
      }

      if (selectedMechanics.length > 0) {
        params.mechanics = selectedMechanics.map(m => m.boardgamemechanic_id).join(',');
      }

      if (selectedCategories.length > 0) {
        params.categories = selectedCategories.map(c => c.boardgamecategory_id).join(',');
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

      const response = await axios.get('http://localhost:8000/games', { params });
      return response.data;
    },
    keepPreviousData: true,
  });

  const { games = [], total = 0 } = response;

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, playerCount, recommendations, selectedDesigners, selectedArtists, selectedMechanics, selectedCategories, weight, sortBy]);

  const handlePageChange = (event, newPage) => {
    setCurrentPage(newPage);
  };

  const handleGameClick = async (game) => {
    try {
      const response = await axios.get(`http://localhost:8000/games/${game.id}`);
      setSelectedGame(response.data);
      setDetailsOpen(true);
    } catch (err) {
      console.error('Failed to fetch game details:', err);
    }
  };

  const handleFilter = (type, id, name) => {
    if (type === 'game') {
      handleGameClick({ id });
    } else if (type === 'designer') {
      setSelectedDesigners(prev => {
        const exists = prev.some(d => d.boardgamedesigner_id === id);
        if (exists) {
          return prev.filter(d => d.boardgamedesigner_id !== id);
        } else {
          return [...prev, { boardgamedesigner_id: id, boardgamedesigner_name: name }];
        }
      });
    } else if (type === 'artist') {
      setSelectedArtists(prev => {
        const exists = prev.some(a => a.boardgameartist_id === id);
        if (exists) {
          return prev.filter(a => a.boardgameartist_id !== id);
        } else {
          return [...prev, { boardgameartist_id: id, boardgameartist_name: name }];
        }
      });
    } else if (type === 'mechanic') {
      setSelectedMechanics(prev => {
        const exists = prev.some(m => m.boardgamemechanic_id === id);
        if (exists) {
          return prev.filter(m => m.boardgamemechanic_id !== id);
        } else {
          return [...prev, { boardgamemechanic_id: id, boardgamemechanic_name: name }];
        }
      });
    } else if (type === 'category') {
      setSelectedCategories(prev => {
        const exists = prev.some(c => c.boardgamecategory_id === id);
        if (exists) {
          return prev.filter(c => c.boardgamecategory_id !== id);
        } else {
          return [...prev, { boardgamecategory_id: id, boardgamecategory_name: name }];
        }
      });
    }
  };

  const handleRemoveFilter = (type, id) => {
    if (type === 'designer') {
      setSelectedDesigners(prev => prev.filter(d => d.boardgamedesigner_id !== id));
    } else if (type === 'artist') {
      setSelectedArtists(prev => prev.filter(a => a.boardgameartist_id !== id));
    } else if (type === 'mechanic') {
      setSelectedMechanics(prev => prev.filter(m => m.boardgamemechanic_id !== id));
    } else if (type === 'category') {
      setSelectedCategories(prev => prev.filter(c => c.boardgamecategory_id !== id));
    }
  };

  const renderFilterChips = () => {
    const chips = [];
    
    selectedDesigners.forEach(designer => {
      chips.push(
        <Chip
          key={`designer-${designer.boardgamedesigner_id}`}
          label={`Designer: ${designer.boardgamedesigner_name}`}
          onDelete={() => handleRemoveFilter('designer', designer.boardgamedesigner_id)}
          color="primary"
          sx={{ m: 0.5 }}
        />
      );
    });
    
    selectedArtists.forEach(artist => {
      chips.push(
        <Chip
          key={`artist-${artist.boardgameartist_id}`}
          label={`Artist: ${artist.boardgameartist_name}`}
          onDelete={() => handleRemoveFilter('artist', artist.boardgameartist_id)}
          color="primary"
          sx={{ m: 0.5 }}
        />
      );
    });

    selectedMechanics.forEach(mechanic => {
      chips.push(
        <Chip
          key={`mechanic-${mechanic.boardgamemechanic_id}`}
          label={`Mechanic: ${mechanic.boardgamemechanic_name}`}
          onDelete={() => handleRemoveFilter('mechanic', mechanic.boardgamemechanic_id)}
          color="primary"
          sx={{ m: 0.5 }}
        />
      );
    });

    selectedCategories.forEach(category => {
      chips.push(
        <Chip
          key={`category-${category.boardgamecategory_id}`}
          label={`Category: ${category.boardgamecategory_name}`}
          onDelete={() => handleRemoveFilter('category', category.boardgamecategory_id)}
          color="primary"
          sx={{ m: 0.5 }}
        />
      );
    });

    return chips.length > 0 ? (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {chips}
      </Box>
    ) : null;
  };

  const renderGameGrid = () => {
    if (isLoading) {
      return (
        <Grid container spacing={2}>
          {Array.from(new Array(12)).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
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
      <Grid container spacing={3}>
        {games.map((game) => (
          <Grid item xs={12} sm={6} md={4} key={game.id}>
            <GameCard
              game={game}
              onClick={() => handleGameClick(game)}
              sortBy={sortBy}
            />
          </Grid>
        ))}
      </Grid>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ my: 4, display: 'flex', gap: 4 }}>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search by game title"
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
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
          {renderFilterChips()}
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
              options={mechanics
                .filter(m => !selectedMechanics.some(sm => sm.boardgamemechanic_id === m.boardgamemechanic_id))
                .sort((a, b) => a.boardgamemechanic_name.localeCompare(b.boardgamemechanic_name))}
              getOptionLabel={(option) => option.boardgamemechanic_name}
              value={[]}
              onChange={(event, newValue) => {
                if (newValue && newValue.length > 0) {
                  const selected = newValue[0];
                  setSelectedMechanics(prev => [...prev, selected]);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  placeholder="Select mechanics"
                />
              )}
              renderOption={(props, option) => (
                <li {...props}>
                  <Typography>{option.boardgamemechanic_name}</Typography>
                </li>
              )}
            />
          </FormControl>
        </Box>
      </Box>
      {total > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={Math.ceil(total / gamesPerPage)}
            page={currentPage}
            onChange={handlePageChange}
            color="primary"
            size={isMobile ? "small" : "large"}
            disabled={isFetching}
          />
        </Box>
      )}
      <GameDetails
        game={selectedGame}
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        onFilter={handleFilter}
      />
    </Container>
  );
};

export default memo(GameList); 