import React, { useRef, useEffect, useState } from 'react';
import { Stage, Layer, Image as KonvaImage, Line } from 'react-konva';
import { Box, Paper, Typography } from '@mui/material';
import Konva from 'konva';

interface ImageCanvasProps {
  imageUrl?: string;
  width: number;
  height: number;
  onAnnotationChange?: (annotations: any[]) => void;
}

const ImageCanvas: React.FC<ImageCanvasProps> = ({
  imageUrl,
  width,
  height,
  onAnnotationChange,
}) => {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentPath, setCurrentPath] = useState<number[]>([]);
  const [paths, setPaths] = useState<any[]>([]);
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

  const handleMouseDown = (e: any) => {
    setIsDrawing(true);
    const pos = e.target.getStage().getPointerPosition();
    setCurrentPath([pos.x, pos.y]);
  };

  const handleMouseMove = (e: any) => {
    if (!isDrawing) return;

    const stage = e.target.getStage();
    const point = stage.getPointerPosition();
    setCurrentPath((prev) => [...prev, point.x, point.y]);
  };

  const handleMouseUp = () => {
    if (!isDrawing) return;
    
    setIsDrawing(false);
    setPaths((prev) => [...prev, { points: currentPath, id: Date.now() }]);
    setCurrentPath([]);
    
    if (onAnnotationChange) {
      onAnnotationChange([...paths, { points: currentPath, id: Date.now() }]);
    }
  };

  const clearAnnotations = () => {
    setPaths([]);
    setCurrentPath([]);
    if (onAnnotationChange) {
      onAnnotationChange([]);
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Image Annotation
        </Typography>
        <Box>
          <button onClick={clearAnnotations}>Clear All</button>
        </Box>
      </Box>
      
      <Box
        sx={{
          border: '1px solid #ccc',
          borderRadius: 1,
          overflow: 'hidden',
          cursor: 'crosshair',
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
            
            {paths.map((path) => (
              <Line
                key={path.id}
                points={path.points}
                stroke="#ff0000"
                strokeWidth={2}
                lineCap="round"
                lineJoin="round"
                globalCompositeOperation="source-over"
              />
            ))}
            
            {isDrawing && (
              <Line
                points={currentPath}
                stroke="#ff0000"
                strokeWidth={2}
                lineCap="round"
                lineJoin="round"
                globalCompositeOperation="source-over"
              />
            )}
          </Layer>
        </Stage>
      </Box>
    </Paper>
  );
};

export default ImageCanvas;