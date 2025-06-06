import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemText,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function GameList() {
  const [games, setGames] = useState([]);
  const [filters, setFilters] = useState({
    designer: '',
    mechanic: '',
    genre: '',
  });
  const [filterOptions, setFilterOptions] = useState({
    designers: [],
    mechanics: [],
    genres: [],
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [isFilterDrawerOpen, setIsFilterDrawerOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();

  useEffect(() => {
    fetchGames();
    fetchFilterOptions();
  }, [filters]);

  const fetchGames = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.designer) params.append('designer', filters.designer);
      if (filters.mechanic) params.append('mechanic', filters.mechanic);
      if (filters.genre) params.append('genre', filters.genre);
      
      const response = await axios.get(`${API_BASE_URL}/games?${params.toString()}`);
      setGames(response.data);
    } catch (error) {
      console.error('Error fetching games:', error);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/filters`);
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    // Implement search logic here
  };

  const filteredGames = games.filter(game =>
    game.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const FilterDrawer = () => (
    <Drawer
      anchor={isMobile ? 'bottom' : 'right'}
      open={isFilterDrawerOpen}
      onClose={() => setIsFilterDrawerOpen(false)}
    >
      <Box sx={{ width: isMobile ? 'auto' : 300, p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <FormControl fullWidth margin="normal">
          <InputLabel>Designer</InputLabel>
          <Select
            value={filters.designer}
            onChange={(e) => handleFilterChange('designer', e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            {filterOptions.designers.map((designer) => (
              <MenuItem key={designer} value={designer}>
                {designer}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Mechanic</InputLabel>
          <Select
            value={filters.mechanic}
            onChange={(e) => handleFilterChange('mechanic', e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            {filterOptions.mechanics.map((mechanic) => (
              <MenuItem key={mechanic} value={mechanic}>
                {mechanic}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Genre</InputLabel>
          <Select
            value={filters.genre}
            onChange={(e) => handleFilterChange('genre', e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            {filterOptions.genres.map((genre) => (
              <MenuItem key={genre} value={genre}>
                {genre}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    </Drawer>
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <IconButton onClick={() => setIsFilterDrawerOpen(true)}>
          <FilterListIcon />
        </IconButton>
      </Box>
      
      <FilterDrawer />
      
      <Grid container spacing={3}>
        {filteredGames.map((game) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={game.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'scale(1.02)',
                  transition: 'transform 0.2s ease-in-out',
                },
              }}
              onClick={() => navigate(`/game/${game.id}`)}
            >
              <CardMedia
                component="img"
                height="200"
                image={game.image_url || '/placeholder.jpg'}
                alt={game.name}
              />
              <CardContent>
                <Typography gutterBottom variant="h6" component="div">
                  {game.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {game.designer}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {game.player_count} • {game.play_time}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default GameList; 