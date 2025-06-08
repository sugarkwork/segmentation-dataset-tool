import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Stage, Layer, Image as KonvaImage, Line, Group } from 'react-konva';
import { 
  Box, 
  Paper, 
  Typography, 
  Toolbar, 
  IconButton, 
  Slider, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Tooltip
} from '@mui/material';
import {
  Brush as BrushIcon,
  Delete as EraseIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Layers as LayersIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import Konva from 'konva';

interface SegmentationLayer {
  id: string;
  name: string;
  paths: any[];
  classId: number;
  className: string;
  color: string;
  visible: boolean;
  locked: boolean;
  opacity: number;
}

interface AdvancedImageCanvasProps {
  imageUrl?: string;
  width: number;
  height: number;
  classes: Array<{id: number; name: string; color: string}>;
  onSegmentationChange?: (layers: SegmentationLayer[]) => void;
}

const AdvancedImageCanvas: React.FC<AdvancedImageCanvasProps> = ({
  imageUrl,
  width,
  height,
  classes,
  onSegmentationChange,
}) => {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState<'brush' | 'eraser'>('brush');
  const [brushSize, setBrushSize] = useState(5);
  const [selectedClassId, setSelectedClassId] = useState<number>(classes[0]?.id || 1);
  const [layers, setLayers] = useState<SegmentationLayer[]>([]);
  const [currentPath, setCurrentPath] = useState<number[]>([]);
  const [history, setHistory] = useState<SegmentationLayer[][]>([]);
  const [historyStep, setHistoryStep] = useState(0);
  const [activeLayerId, setActiveLayerId] = useState<string>('');
  
  const stageRef = useRef<Konva.Stage>(null);

  useEffect(() => {
    if (imageUrl) {
      const img = new window.Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        setImage(img);
      };
      img.src = imageUrl;
    }
  }, [imageUrl]);

  const saveToHistory = useCallback(() => {
    const newHistory = history.slice(0, historyStep + 1);
    newHistory.push(JSON.parse(JSON.stringify(layers)));
    setHistory(newHistory);
    setHistoryStep(newHistory.length - 1);
  }, [history, historyStep, layers]);

  const undo = useCallback(() => {
    if (historyStep > 0) {
      setHistoryStep(historyStep - 1);
      setLayers(history[historyStep - 1]);
    }
  }, [history, historyStep]);

  const redo = useCallback(() => {
    if (historyStep < history.length - 1) {
      setHistoryStep(historyStep + 1);
      setLayers(history[historyStep + 1]);
    }
  }, [history, historyStep]);

  const createNewLayer = useCallback((classId: number) => {
    const selectedClass = classes.find(c => c.id === classId);
    if (!selectedClass) return '';
    
    const newLayer: SegmentationLayer = {
      id: `layer_${Date.now()}`,
      name: `${selectedClass.name}_${layers.length + 1}`,
      paths: [],
      classId: classId,
      className: selectedClass.name,
      color: selectedClass.color,
      visible: true,
      locked: false,
      opacity: 0.7
    };
    
    setLayers(prev => [...prev, newLayer]);
    return newLayer.id;
  }, [classes, layers.length]);

  const handleMouseDown = (e: any) => {
    if (tool === 'eraser' || layers.find(l => l.id === activeLayerId)?.locked) return;
    
    setIsDrawing(true);
    const pos = e.target.getStage().getPointerPosition();
    setCurrentPath([pos.x, pos.y]);
    
    if (!activeLayerId) {
      const newLayerId = createNewLayer(selectedClassId);
      setActiveLayerId(newLayerId);
    }
  };

  const handleMouseMove = (e: any) => {
    if (!isDrawing) return;

    const stage = e.target.getStage();
    const point = stage.getPointerPosition();
    setCurrentPath(prev => [...prev, point.x, point.y]);
  };

  const handleMouseUp = () => {
    if (!isDrawing) return;
    
    setIsDrawing(false);
    
    if (currentPath.length > 0 && activeLayerId) {
      setLayers(prev => prev.map(layer => {
        if (layer.id === activeLayerId) {
          return {
            ...layer,
            paths: [...layer.paths, {
              points: currentPath,
              id: Date.now(),
              tool: tool,
              brushSize: brushSize
            }]
          };
        }
        return layer;
      }));
      
      saveToHistory();
    }
    
    setCurrentPath([]);
  };

  const toggleLayerVisibility = (layerId: string) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, visible: !layer.visible }
        : layer
    ));
  };

  const toggleLayerLock = (layerId: string) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, locked: !layer.locked }
        : layer
    ));
  };

  const updateLayerOpacity = (layerId: string, opacity: number) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, opacity: opacity / 100 }
        : layer
    ));
  };

  const deleteLayer = (layerId: string) => {
    setLayers(prev => prev.filter(layer => layer.id !== layerId));
    if (activeLayerId === layerId) {
      setActiveLayerId('');
    }
  };

  const clearAllLayers = () => {
    saveToHistory();
    setLayers([]);
    setActiveLayerId('');
  };

  useEffect(() => {
    if (onSegmentationChange) {
      onSegmentationChange(layers);
    }
  }, [layers, onSegmentationChange]);

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      {/* Main Canvas Area */}
      <Box sx={{ flexGrow: 1 }}>
        <Paper sx={{ p: 2 }}>
          {/* Toolbar */}
          <Toolbar variant="dense" sx={{ mb: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Tooltip title="Brush Tool">
              <IconButton
                color={tool === 'brush' ? 'primary' : 'default'}
                onClick={() => setTool('brush')}
              >
                <BrushIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Eraser Tool">
              <IconButton
                color={tool === 'eraser' ? 'primary' : 'default'}
                onClick={() => setTool('eraser')}
              >
                <EraseIcon />
              </IconButton>
            </Tooltip>
            
            <Box sx={{ mx: 2, width: 120 }}>
              <Typography variant="caption" gutterBottom>
                Brush Size: {brushSize}
              </Typography>
              <Slider
                value={brushSize}
                onChange={(_, value) => setBrushSize(value as number)}
                min={1}
                max={50}
                size="small"
              />
            </Box>
            
            <FormControl size="small" sx={{ minWidth: 120, mr: 2 }}>
              <InputLabel>Class</InputLabel>
              <Select
                value={selectedClassId}
                onChange={(e) => setSelectedClassId(e.target.value as number)}
                label="Class"
              >
                {classes.map((cls) => (
                  <MenuItem key={cls.id} value={cls.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          bgcolor: cls.color,
                          borderRadius: '50%',
                          mr: 1
                        }}
                      />
                      {cls.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Tooltip title="Undo">
              <IconButton
                onClick={undo}
                disabled={historyStep <= 0}
              >
                <UndoIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Redo">
              <IconButton
                onClick={redo}
                disabled={historyStep >= history.length - 1}
              >
                <RedoIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Clear All">
              <IconButton
                onClick={clearAllLayers}
                color="error"
              >
                <ClearIcon />
              </IconButton>
            </Tooltip>
          </Toolbar>
          
          {/* Canvas */}
          <Box
            sx={{
              border: '1px solid #ccc',
              borderRadius: 1,
              overflow: 'hidden',
              cursor: tool === 'brush' ? 'crosshair' : 'grab',
            }}
          >
            <Stage
              width={width}
              height={height}
              onMouseDown={handleMouseDown}
              onMousemove={handleMouseMove}
              onMouseup={handleMouseUp}
              ref={stageRef}
            >
              <Layer>
                {image && (
                  <KonvaImage
                    image={image}
                    width={width}
                    height={height}
                    listening={false}
                  />
                )}
              </Layer>
              
              {/* Segmentation Layers */}
              {layers.map((layer) => (
                <Layer
                  key={layer.id}
                  visible={layer.visible}
                  opacity={layer.opacity}
                >
                  <Group>
                    {layer.paths.map((path) => (
                      <Line
                        key={path.id}
                        points={path.points}
                        stroke={layer.color}
                        strokeWidth={path.brushSize || brushSize}
                        lineCap="round"
                        lineJoin="round"
                        globalCompositeOperation={
                          path.tool === 'eraser' ? 'destination-out' : 'source-over'
                        }
                      />
                    ))}
                  </Group>
                </Layer>
              ))}
              
              {/* Current drawing path */}
              {isDrawing && currentPath.length > 0 && (
                <Layer>
                  <Line
                    points={currentPath}
                    stroke={classes.find(c => c.id === selectedClassId)?.color || '#ff0000'}
                    strokeWidth={brushSize}
                    lineCap="round"
                    lineJoin="round"
                    globalCompositeOperation={
                      tool === 'eraser' ? 'destination-out' : 'source-over'
                    }
                  />
                </Layer>
              )}
            </Stage>
          </Box>
        </Paper>
      </Box>
      
      {/* Layer Panel */}
      <Box sx={{ width: 280, ml: 2 }}>
        <Paper sx={{ p: 2, height: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <LayersIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Layers</Typography>
          </Box>
          
          <Stack spacing={1} sx={{ maxHeight: 400, overflow: 'auto' }}>
            {layers.map((layer, index) => (
              <Paper
                key={layer.id}
                variant="outlined"
                sx={{
                  p: 1,
                  bgcolor: activeLayerId === layer.id ? 'primary.50' : 'transparent',
                  cursor: 'pointer'
                }}
                onClick={() => setActiveLayerId(layer.id)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Chip
                    label={layer.className}
                    size="small"
                    sx={{ 
                      bgcolor: layer.color,
                      color: 'white',
                      fontWeight: 'bold',
                      mr: 1
                    }}
                  />
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>
                    {layer.name}
                  </Typography>
                  
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleLayerVisibility(layer.id);
                    }}
                  >
                    {layer.visible ? <VisibilityIcon /> : <VisibilityOffIcon />}
                  </IconButton>
                  
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleLayerLock(layer.id);
                    }}
                  >
                    {layer.locked ? <LockIcon /> : <LockOpenIcon />}
                  </IconButton>
                  
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteLayer(layer.id);
                    }}
                  >
                    <EraseIcon />
                  </IconButton>
                </Box>
                
                <Box sx={{ px: 1 }}>
                  <Typography variant="caption" gutterBottom>
                    Opacity: {Math.round(layer.opacity * 100)}%
                  </Typography>
                  <Slider
                    value={layer.opacity * 100}
                    onChange={(_, value) => updateLayerOpacity(layer.id, value as number)}
                    min={0}
                    max={100}
                    size="small"
                  />
                </Box>
              </Paper>
            ))}
            
            {layers.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
                No layers yet. Start drawing to create your first segmentation layer.
              </Typography>
            )}
          </Stack>
        </Paper>
      </Box>
    </Box>
  );
};

export default AdvancedImageCanvas;