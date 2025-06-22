import React, { useState, memo } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PsychologyAltOutlinedIcon from '@mui/icons-material/PsychologyAltOutlined';
import StarBorderOutlinedIcon from '@mui/icons-material/StarBorderOutlined';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';

const GameCard = memo(({ game, onClick, sortBy, liked, disliked, onLike, onDislike }) => {
  const [bgColor, setBgColor] = useState('#f5f5f5');
  const [imageSrc, setImageSrc] = useState(() => {
    if (!game.image) return '/placeholder.png';
    const filename = game.image.split('/').pop();
    return `http://localhost:8000/images/${filename}`;
  });

  const handleImageError = () => {
    if (game.image) {
      setImageSrc(`http://localhost:8000/proxy-image/${encodeURIComponent(game.image)}`);
    } else {
      setImageSrc('/placeholder.png');
    }
  };

  const handleLikeClick = (e) => {
    e.stopPropagation();
    onLike();
  };

  const handleDislikeClick = (e) => {
    e.stopPropagation();
    onDislike();
  };

  const handleImageLoad = (event) => {
    const img = event.target;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    
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
    
    const lighten = (color) => Math.min(255, Math.floor(color * 1.2));
    setBgColor(`rgba(${lighten(r)}, ${lighten(g)}, ${lighten(b)}, 0.3)`);
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        '&:hover': {
          boxShadow: 6
        },
      }}
    >
      <Box 
        onClick={onClick} 
        sx={{ 
          display: 'flex', 
          flexDirection: 'row', 
          flexGrow: 1, 
          textDecoration: 'none', 
          color: 'inherit', 
          cursor: 'pointer',
          minWidth: 0 // important for ellipsis
        }}
      >
        <CardMedia
          component="img"
          sx={{ 
            width: 120,
            height: 160,
            objectFit: 'contain',
            backgroundColor: bgColor,
            transition: 'background-color 0.3s ease',
            flexShrink: 0,
            alignSelf: 'center'
          }}
          image={imageSrc}
          alt={game.name}
          loading="lazy"
          crossOrigin="anonymous"
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
        <CardContent sx={{ 
          flexGrow: 1, 
          p: 1, 
          display: 'flex', 
          flexDirection: 'column',
          minWidth: 0,
        }}>
          <Typography 
            variant="h4" 
            sx={{ 
              fontSize: '1.2rem', 
              mb: 0.5,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {game.name}
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <PeopleIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {game.min_players === game.max_players ? game.min_players : `${game.min_players} - ${game.max_players}`} players
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
              <StarBorderOutlinedIcon sx={{ fontSize: '1rem', color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {game.average ? game.average.toFixed(1) : 'N/A'}
                {sortBy === 'recommendation_score' && game.recommendation_score && ` (${(game.recommendation_score * 100).toFixed(0)}%)`}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', p: 0.5, borderLeft: '1px solid', borderColor: 'divider' }}>
        <IconButton onClick={handleLikeClick} size="small">
          {liked ? <ThumbUpIcon color="success" /> : <ThumbUpOutlinedIcon />}
        </IconButton>
        <IconButton onClick={handleDislikeClick} size="small">
          {disliked ? <ThumbDownIcon color="error" /> : <ThumbDownOutlinedIcon />}
        </IconButton>
      </Box>
    </Card>
  );
});

export default GameCard; 