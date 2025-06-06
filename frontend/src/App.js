import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Typography, Box } from '@mui/material';
import GameList from './components/GameList';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 3, mb: 4 }}>
          <Container>
            <Typography variant="h3" component="h1" gutterBottom>
              Board Game Recommender
            </Typography>
            <Typography variant="subtitle1">
              Discover and explore board games
            </Typography>
          </Container>
        </Box>
        <GameList />
      </div>
    </ThemeProvider>
  );
}

export default App; 