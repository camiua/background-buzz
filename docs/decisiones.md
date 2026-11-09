# Decisiones y aprendizajes

Las decisiones de arquitectura están en la spec (`.specify/1_spec.md` §1.3). Aquí se amplían las que lo necesitan y se recogen los aprendizajes del proyecto.

## Aprendizajes

### Nivel Esencial

- **Transfer learning:** YOLO11 nano, preentrenado en COCO, aprendió a encontrar los logos en unas 7 épocas y en 7 minutos de GPU. Lo que más tardó en mejorar fue el ajuste de las cajas (mAP50-95).
- **Parada anticipada:** con `patience = 20`, el entrenamiento se detuvo en la época 81 y guardó como `best.pt` la de la época 61, justo antes de empezar a sobreajustar.
- **Un 0,995 en test no es un modelo perfecto:** el test era un solo vídeo del mismo entorno que el entrenamiento. Con una captura de un stream real, el modelo no detectó una lata Monster de otra variante.
- **El modelo aprende colores y contrastes, no formas abstractas:** solo vio la lata rosa de Monster, con la garra oscura sobre fondo rosa. La garra verde sobre fondo negro es, para la red, un patrón distinto. Desactivar el cambio de tono (`hsv_h = 0`) en el aumento de datos probablemente empeoró esta generalización.
- **El umbral de confianza filtra las dudas:** el modelo confundió el avatar rojo de TikTok con la llama de Burn con una confianza de 0,47. Con el umbral de 0,5, esa detección se descarta.
- **Reparto por vídeo:** los fotogramas de un mismo vídeo son casi iguales. Repartirlos entre entrenamiento y test daría métricas falsamente altas (fuga de datos).
- **Letterbox:** las imágenes se redimensionan a 640 × 640 sin deformarse, con bandas negras. Las cajas se convierten después a las coordenadas de la imagen original.
- **pre-commit y el área de preparación de Git:** si un hook modifica un archivo, el commit se cancela. Hay que volver a hacer `git add` de ese archivo antes de repetir el commit.
- **Entornos virtuales fuera de OneDrive:** PyTorch son miles de archivos; dentro de una carpeta sincronizada, la instalación es lenta y puede fallar. El entorno se guarda fuera con `UV_PROJECT_ENVIRONMENT`.
