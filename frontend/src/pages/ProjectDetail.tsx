import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Typography, 
  Box, 
  Grid, 
  Paper, 
  List, 
  ListItem, 
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import { 
  Image as ImageIcon, 
  Add as AddIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import AdvancedImageCanvas from '../components/AdvancedImageCanvas';
import ImageUpload from '../components/ImageUpload';
import { projectsApi, imagesApi, classesApi } from '../services/api';
import { Project, Image, ClassDefinition } from '../types';

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [images, setImages] = useState<Image[]>([]);
  const [classes, setClasses] = useState<ClassDefinition[]>([]);
  const [selectedImage, setSelectedImage] = useState<Image | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [showClassDialog, setShowClassDialog] = useState(false);
  const [newClassName, setNewClassName] = useState('');
  const [newClassColor, setNewClassColor] = useState('#FF0000');

  useEffect(() => {
    if (id) {
      loadProjectData(parseInt(id));
    }
  }, [id]);

  const loadProjectData = async (projectId: number) => {
    try {
      const [projectData, imagesData, classesData] = await Promise.all([
        projectsApi.getProject(projectId),
        imagesApi.getProjectImages(projectId),
        classesApi.getProjectClasses(projectId)
      ]);
      
      setProject(projectData);
      setImages(imagesData);
      setClasses(classesData);
      
      if (imagesData.length > 0 && !selectedImage) {
        setSelectedImage(imagesData[0]);
      }
    } catch (error) {
      console.error('Failed to load project data:', error);
    }
  };

  const handleImageUpload = async (files: File[]) => {
    if (!project) return;
    
    try {
      for (const file of files) {
        await imagesApi.uploadImage(project.id, file);
      }
      // Reload images
      const imagesData = await imagesApi.getProjectImages(project.id);
      setImages(imagesData);
      setShowUpload(false);
    } catch (error) {
      console.error('Failed to upload images:', error);
    }
  };

  const handleCreateClass = async () => {
    if (!project || !newClassName) return;
    
    try {
      await classesApi.createClass(project.id, newClassName, newClassColor);
      const classesData = await classesApi.getProjectClasses(project.id);
      setClasses(classesData);
      setShowClassDialog(false);
      setNewClassName('');
      setNewClassColor('#FF0000');
    } catch (error) {
      console.error('Failed to create class:', error);
    }
  };

  const handleSegmentationChange = (layers: any[]) => {
    // Handle segmentation changes here
    console.log('Segmentation layers updated:', layers);
    // TODO: Save to backend
  };

  if (!project) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {project.name}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            sx={{ mr: 1 }}
          >
            Export Dataset
          </Button>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
          >
            Settings
          </Button>
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        {/* Main Canvas Area */}
        <Grid item xs={12} lg={8}>
          {selectedImage ? (
            <AdvancedImageCanvas
              imageUrl={`/uploads/${project.id}/${selectedImage.filename}`}
              width={800}
              height={600}
              classes={classes}
              onSegmentationChange={handleSegmentationChange}
            />
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No image selected
              </Typography>
              <Typography color="text.secondary" gutterBottom>
                Select an image from the sidebar or upload new images to get started.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowUpload(true)}
              >
                Upload Images
              </Button>
            </Paper>
          )}
        </Grid>
        
        {/* Sidebar */}
        <Grid item xs={12} lg={4}>
          <Grid container spacing={2}>
            {/* Images */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Images ({images.length})
                  </Typography>
                  <IconButton onClick={() => setShowUpload(true)}>
                    <AddIcon />
                  </IconButton>
                </Box>
                
                <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {images.map((image) => (
                    <ListItem
                      key={image.id}
                      button
                      selected={selectedImage?.id === image.id}
                      onClick={() => setSelectedImage(image)}
                    >
                      <ListItemAvatar>
                        <Avatar>
                          <ImageIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={image.original_filename}
                        secondary={
                          <Box>
                            <Chip
                              label={image.dataset_type}
                              size="small"
                              variant="outlined"
                              sx={{ mr: 1 }}
                            />
                            <Chip
                              label={`${image.width}x${image.height}`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
            
            {/* Classes */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Classes ({classes.length})
                  </Typography>
                  <IconButton onClick={() => setShowClassDialog(true)}>
                    <AddIcon />
                  </IconButton>
                </Box>
                
                <List dense>
                  {classes.map((cls) => (
                    <ListItem key={cls.id}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: cls.color, width: 24, height: 24 }}>
                          {cls.class_index}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={cls.display_name}
                        secondary={cls.name}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Upload Dialog */}
      <Dialog open={showUpload} onClose={() => setShowUpload(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Images</DialogTitle>
        <DialogContent>
          <ImageUpload onUpload={handleImageUpload} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUpload(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Class Creation Dialog */}
      <Dialog open={showClassDialog} onClose={() => setShowClassDialog(false)}>
        <DialogTitle>Create New Class</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Class Name"
            fullWidth
            variant="outlined"
            value={newClassName}
            onChange={(e) => setNewClassName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              label="Color"
              type="color"
              value={newClassColor}
              onChange={(e) => setNewClassColor(e.target.value)}
              sx={{ mr: 2 }}
            />
            <Box
              sx={{
                width: 40,
                height: 40,
                bgcolor: newClassColor,
                border: '1px solid #ccc',
                borderRadius: 1
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowClassDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateClass} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProjectDetail;