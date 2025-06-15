import React, { useState, memo } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PsychologyAltOutlinedIcon from '@mui/icons-material/PsychologyAltOutlined';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarBorderOutlinedIcon from '@mui/icons-material/StarBorderOutlined';

const GameCard = memo(({ game, onClick, sortBy }) => {
  const [bgColor, setBgColor] = useState('#f5f5f5');

  const handleImageLoad = (event) => {
    const img = event.target;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    
    // Get the average color from the image
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let r = 0, g = 0, b = 0;
    const total = imageData.length / 4;
    
    for (let i = 0; i < imageData.length; i += 4) {
      r += imageData[i];
      g += imageData[i + 1];
      b += imageData[i + 2];
    }
    
    r = Math.floor(r / total);
    g = Math.floor(g / total);
    b = Math.floor(b / total);
    
    // Convert to a lighter shade for the background
    const lighten = (color) => Math.min(255, Math.floor(color * 1.2));
    setBgColor(`rgba(${lighten(r)}, ${lighten(g)}, ${lighten(b)}, 0.3)`);
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        width: '100%',
        maxWidth: '100%',
        display: 'flex',
        flexDirection: 'row',
        cursor: 'pointer',
        '&:hover': {
          boxShadow: 6
        }
      }}
      onClick={onClick}
    >
      <CardMedia
        component="img"
        sx={{ 
          width: 140,
          height: 200,
          objectFit: 'contain',
          backgroundColor: bgColor,
          transition: 'background-color 0.3s ease',
          flexShrink: 0
        }}
        image={game.image ? `http://localhost:8000/proxy-image/${encodeURIComponent(game.image)}` : '/placeholder.png'}
        alt={game.name}
        loading="lazy"
        crossOrigin="anonymous"
        onLoad={handleImageLoad}
      />
      <CardContent sx={{ 
        flexGrow: 1, 
        p: 1, 
        display: 'flex', 
        flexDirection: 'column',
        minWidth: 0,
        maxWidth: 'calc(100% - 140px)'  // Account for image width
      }}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontSize: '1.2rem', 
            mb: 0.5,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            width: '100%',
            display: 'block',
            minWidth: 0  // This is crucial for text overflow to work
          }}
        >
          {game.name}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <PeopleIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {game.min_players === game.max_players ? game.min_players : `${game.min_players} - ${game.max_players} players`}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <AccessTimeIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {game.min_playtime === game.max_playtime ? `${game.min_playtime} min` : `${game.min_playtime} - ${game.max_playtime} min`}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <PsychologyAltOutlinedIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {game.average_weight ? `${game.average_weight.toFixed(1)}/5` : 'N/A'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <EmojiEventsIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {game[sortBy] || 'Unranked'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <StarBorderOutlinedIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {game.average ? game.average.toFixed(1) : 'N/A'}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
});

export default GameCard; 