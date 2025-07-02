import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Link } from 'react-router-dom';
import AppRoutes from './routes/appRoutes';
import { AppBar, Toolbar, Typography, Button, Container, Box } from '@mui/material';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              在线考试系统
            </Typography>
            <Button color="inherit" component={Link} to="/users">
              用户管理
            </Button>
            <Button color="inherit" component={Link} to="/exams">
              考试管理
            </Button>
          </Toolbar>
        </AppBar>
        
        <Container sx={{ mt: 3 }}>
          <AppRoutes />
        </Container>
      </Box>
    </Router>
  );
}

export default App;