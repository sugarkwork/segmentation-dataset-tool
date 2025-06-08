import React from 'react';
import { Typography, Grid, Card, CardContent, Button, Box } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Your Projects
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          New Project
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Sample Project
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Description of the sample project for segmentation dataset creation.
              </Typography>
              <Typography variant="caption" display="block" sx={{ mt: 2 }}>
                Images: 0 | Classes: 0 | Progress: 0%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;