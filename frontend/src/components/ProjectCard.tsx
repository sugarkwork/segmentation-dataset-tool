import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  LinearProgress,
  Box,
  Chip,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ProjectSummary } from '../types';

interface ProjectCardProps {
  project: ProjectSummary;
  onEdit?: (project: ProjectSummary) => void;
  onDelete?: (project: ProjectSummary) => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onEdit, onDelete }) => {
  const navigate = useNavigate();

  const handleOpen = () => {
    navigate(`/projects/${project.id}`);
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {project.name}
        </Typography>
        
        {project.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {project.description}
          </Typography>
        )}
        
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
            <Chip
              label={`${project.image_count} Images`}
              size="small"
              variant="outlined"
            />
            <Chip
              label={`${project.class_count} Classes`}
              size="small"
              variant="outlined"
            />
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Typography variant="caption" sx={{ mr: 1 }}>
              Progress:
            </Typography>
            <LinearProgress
              variant="determinate"
              value={project.completion_percentage}
              sx={{ flexGrow: 1, mr: 1 }}
            />
            <Typography variant="caption">
              {project.completion_percentage}%
            </Typography>
          </Box>
        </Box>
        
        <Typography variant="caption" color="text.secondary">
          Created: {new Date(project.created_at).toLocaleDateString()}
        </Typography>
      </CardContent>
      
      <CardActions>
        <Button size="small" onClick={handleOpen}>
          Open
        </Button>
        {onEdit && (
          <Button size="small" onClick={() => onEdit(project)}>
            Edit
          </Button>
        )}
        {onDelete && (
          <Button size="small" color="error" onClick={() => onDelete(project)}>
            Delete
          </Button>
        )}
      </CardActions>
    </Card>
  );
};

export default ProjectCard;