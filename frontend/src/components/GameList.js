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
  Stack,
  Popover,
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
import SortIcon from '@mui/icons-material/Sort';
import GameDetails from './GameDetails';
import GameCard from './GameCard';
import ConstructionIcon from '@mui/icons-material/Construction';
import CategoryIcon from '@mui/icons-material/Category';

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
  { value: 'wargames_rank', label: 'Wargames' },
  { value: 'name_asc', label: 'Name (A-Z)' },
  { value: 'name_desc', label: 'Name (Z-A)' }
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
  const [playerOptions, setPlayerOptions] = useState({ count: null, recommendation: 'allowed' });
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
  const [activeFilter, setActiveFilter] = useState(null);

  const handleToggleFilter = (filter) => {
    setActiveFilter(prev => (prev === filter ? null : filter));
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setPlayerOptions({ count: null, recommendation: 'allowed' });
    setWeight({ beginner: false, midweight: false, heavy: false });
    setSelectedMechanics([]);
    setSelectedCategories([]);
    setSortBy('rank');
    setActiveFilter(null);
    setCurrentPage(1);
  };

  const handlePlayerCountChange = (event, newCount) => {
    setPlayerOptions(prev => ({
      ...prev,
      count: newCount,
    }));
  };

  const handlePlayerRecChange = (event, newRec) => {
    if (newRec !== null) {
      setPlayerOptions(prev => ({ ...prev, recommendation: newRec }));
    }
  };

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

  // Fetch mechanics by frequency
  const { data: popularMechanics = [] } = useQuery({
    queryKey: ['mechanics_by_frequency'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/mechanics/by_frequency');
      return response.data;
    },
    staleTime: 24 * 60 * 60 * 1000, // 24 hours
  });

  const { data: popularCategories = [] } = useQuery({
    queryKey: ['categories_by_frequency'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/categories/by_frequency');
      return response.data;
    },
    staleTime: 24 * 60 * 60 * 1000, // 24 hours
  });

  // Fetch games with filters
  const { data: response = { games: [], total: 0 }, isLoading, error, isFetching } = useQuery({
    queryKey: ['games', searchTerm, playerOptions, selectedDesigners, selectedArtists, selectedMechanics, selectedCategories, weight, sortBy, currentPage],
    queryFn: async () => {
      const params = {
        limit: gamesPerPage,
        skip: (currentPage - 1) * gamesPerPage,
        sort_by: sortBy
      };

      if (searchTerm) params.search = searchTerm;

      if (playerOptions.count) {
        params.players = playerOptions.count;
        if (playerOptions.recommendation && playerOptions.recommendation !== 'allowed') {
          params.recommendations = playerOptions.recommendation;
        }
      }

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
  }, [searchTerm, playerOptions, selectedDesigners, selectedArtists, selectedMechanics, selectedCategories, weight, sortBy]);

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
      <Box sx={{ width: '100%', overflow: 'hidden' }}>
        <Grid container spacing={3} sx={{ width: '100%', margin: 0 }}>
          {games.map((game) => (
            <Grid item xs={12} sm={6} md={4} key={game.id} sx={{ width: '100%', padding: '12px !important' }}>
              <Box sx={{ width: '100%', height: '100%' }}>
                <GameCard
                  game={game}
                  onClick={() => handleGameClick(game)}
                  sortBy={sortBy}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4, width: '100%' }}>
      <Stack spacing={2} sx={{ mb: 4 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
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
        </Stack>

        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ flexWrap: 'wrap', gap: 1 }}>
          <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
            <Button
              variant={activeFilter === 'sort' ? 'contained' : 'outlined'}
              onClick={() => handleToggleFilter('sort')}
              startIcon={<SortIcon />}
            >
              Sort
            </Button>
            <Button
              variant={activeFilter === 'players' ? 'contained' : 'outlined'}
              onClick={() => handleToggleFilter('players')}
              startIcon={<PeopleIcon />}
            >
              Players
            </Button>
            <Button
              variant={activeFilter === 'weight' ? 'contained' : 'outlined'}
              onClick={() => handleToggleFilter('weight')}
              startIcon={<PsychologyAltOutlinedIcon />}
            >
              Weight
            </Button>
            <Button
              variant={activeFilter === 'mechanics' ? 'contained' : 'outlined'}
              onClick={() => handleToggleFilter('mechanics')}
              startIcon={<ConstructionIcon />}
            >
              Mechanics
            </Button>
            <Button
              variant={activeFilter === 'categories' ? 'contained' : 'outlined'}
              onClick={() => handleToggleFilter('categories')}
              startIcon={<CategoryIcon />}
            >
              Categories
            </Button>
          </Stack>
          <Button variant="text" onClick={handleResetFilters}>Reset Filters</Button>
        </Stack>
        {activeFilter && (
          <Stack spacing={1} sx={{ mt: 1, gap: 1 }}>
            {activeFilter === 'sort' && (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {sortOptions.map(option => (
                  <Button
                    key={option.value}
                    variant={sortBy === option.value ? 'contained' : 'outlined'}
                    onClick={() => setSortBy(option.value)}
                    size="small"
                  >
                    {option.label}
                  </Button>
                ))}
              </Box>
            )}
            {activeFilter === 'players' && (
              <Stack spacing={1} sx={{ gap: 1 }}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Button
                    variant={playerOptions.count === null ? 'contained' : 'outlined'}
                    onClick={() => handlePlayerCountChange(null, null)}
                    size="small"
                  >
                    Any
                  </Button>
                  {playerCountOptions.map(count => (
                    <Button
                      key={count}
                      variant={playerOptions.count === count ? 'contained' : 'outlined'}
                      onClick={() => handlePlayerCountChange(null, count)}
                      size="small"
                    >
                      {count}
                    </Button>
                  ))}
                </Box>
                {playerOptions.count && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Button size="small" variant={playerOptions.recommendation === 'allowed' ? 'contained' : 'outlined'} onClick={() => handlePlayerRecChange(null, 'allowed')}>Allowed</Button>
                    <Button size="small" variant={playerOptions.recommendation === 'recommended' ? 'contained' : 'outlined'} onClick={() => handlePlayerRecChange(null, 'recommended')}>Recommended</Button>
                    <Button size="small" variant={playerOptions.recommendation === 'best' ? 'contained' : 'outlined'} onClick={() => handlePlayerRecChange(null, 'best')}>Best</Button>
                  </Box>
                )}
              </Stack>
            )}
            {activeFilter === 'weight' && (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Button size="small" variant={weight.beginner ? 'contained' : 'outlined'} onClick={() => setWeight(w => ({ ...w, beginner: !w.beginner }))}>Beginner Friendly (≤ 2.0)</Button>
                <Button size="small" variant={weight.midweight ? 'contained' : 'outlined'} onClick={() => setWeight(w => ({ ...w, midweight: !w.midweight }))}>Midweight (2.0 - 4.0)</Button>
                <Button size="small" variant={weight.heavy ? 'contained' : 'outlined'} onClick={() => setWeight(w => ({ ...w, heavy: !w.heavy }))}>Heavy Cardboard (≥ 4.0)</Button>
              </Box>
            )}
            {activeFilter === 'mechanics' && (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {popularMechanics.map(mech => (
                  <Button
                    key={mech.boardgamemechanic_id}
                    variant={selectedMechanics.some(m => m.boardgamemechanic_id === mech.boardgamemechanic_id) ? 'contained' : 'outlined'}
                    onClick={() => {
                      const isSelected = selectedMechanics.some(m => m.boardgamemechanic_id === mech.boardgamemechanic_id);
                      if (isSelected) {
                        setSelectedMechanics(selectedMechanics.filter(m => m.boardgamemechanic_id !== mech.boardgamemechanic_id));
                      } else {
                        setSelectedMechanics([...selectedMechanics, mech]);
                      }
                    }}
                    size="small"
                  >
                    {mech.boardgamemechanic_name}
                  </Button>
                ))}
              </Box>
            )}
            {activeFilter === 'categories' && (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {popularCategories.map(cat => (
                  <Button
                    key={cat.boardgamecategory_id}
                    variant={selectedCategories.some(c => c.boardgamecategory_id === cat.boardgamecategory_id) ? 'contained' : 'outlined'}
                    onClick={() => {
                      const isSelected = selectedCategories.some(c => c.boardgamecategory_id === cat.boardgamecategory_id);
                      if (isSelected) {
                        setSelectedCategories(selectedCategories.filter(c => c.boardgamecategory_id !== cat.boardgamecategory_id));
                      } else {
                        setSelectedCategories([...selectedCategories, cat]);
                      }
                    }}
                    size="small"
                  >
                    {cat.boardgamecategory_name}
                  </Button>
                ))}
              </Box>
            )}
          </Stack>
        )}
        {renderFilterChips()}
      </Stack>

      {renderGameGrid()}

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