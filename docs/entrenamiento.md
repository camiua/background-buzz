# Entrenamiento del modelo

Evolución del detector de logos de Background Buzz, versión a versión: datos, decisiones, hiperparámetros y métricas. Spec: `.specify/1_spec.md` §1.8 (dataset) y §1.11 (evaluación).

## Modelo v1 · `v1-2-marcas-e100`

| Campo | Valor |
|---|---|
| Fecha | 8 de noviembre de 2026 |
| Clases | `burn`, `monster` (Red Bull queda para la v2: aún no hay imágenes) |
| Modelo base | YOLO11 nano (`yolo11n.pt`, preentrenado en COCO) |
| Dataset | Roboflow `background-buzz`, versión 1 (`v1-2-marcas`) |
| Notebook | `notebooks/train_yolo.ipynb`, ejecutado en Kaggle con una GPU Tesla T4 |
| Librerías | Ultralytics 8.4.191, PyTorch 2.11.0 + CUDA 12.8 |
| Pesos | `best-v1-2-marcas-e100.pt` (5,5 MB). No se suben al repositorio: se publican como asset de la release `v1-esencial` |

### Dataset

**Procedencia.** Vídeos grabados con el móvil en una mesa con un monitor y un portátil, como el escritorio de un streamer. Roboflow extrae unos 25 fotogramas de cada vídeo. Todas las imágenes son propias.

**Etiquetado.** Una caja ajustada solo al **símbolo** del logo: la garra de Monster y la llama de Burn, sin las palabras. Si una mano, un vaso o el borde de la imagen tapan parte del logo, la caja cubre la parte visible. Si el logo no se reconoce (lejos, muy oscuro o casi tapado), la imagen va sin caja. Vasos, tazas y Coca-Cola nunca llevan caja.

**Reparto.** Cada vídeo va entero a un solo conjunto, para que fotogramas casi iguales no queden a la vez en entrenamiento y en test (fuga de datos).

| Conjunto | Lotes (vídeos) | Imágenes |
|---|---|---|
| Entrenamiento | `monster-1-mano`, `monster-4-lejos`, `burn-1-mano`, `burn-2-cerca`, `burn-3-poca-luz`, `juntas-2-3`, `negativo-1` | 191 |
| Validación | `monster-2-cerca`, `burn-4-lejos` | 49 |
| Test | `juntas-1` (las dos marcas, con vaso y taza) | 29 |
| **Total** | | **269** |

**Cajas por marca y conjunto** (cada imagen tiene como mucho una lata de cada marca, así que cajas = imágenes con esa marca):

| Clase | Entrenamiento | Validación | Test | Total |
|---|---|---|---|---|
| `burn` | 118 | 25 | 29 | 172 |
| `monster` | 93 | 24 | 29 | 146 |
| Sin caja a propósito (negativos) | 26 | 0 | 0 | 26 |

Las dos marcas superan el mínimo de 100 imágenes de la spec §1.8. Validación y test no tienen negativos: el reparto por vídeo deja todo `negativo-1` en entrenamiento.

**Descartado:** el lote `monster-3-poca-luz` (23 imágenes). Con la habitación a oscuras el logo no se distingue, y un stream siempre está iluminado, así que no representa el caso de uso. La penumbra con la luz del monitor (`burn-3-poca-luz`) sí se mantiene: el logo se ve y es habitual en un escritorio de gaming. También se excluyó una imagen dudosa de `burn-1-mano`.

### Preprocesado y aumento de datos

**Preprocesado (Roboflow, todas las imágenes):**

| Paso | Valor | Motivo |
|---|---|---|
| Auto-Orient | Activado | Corrige las fotos del móvil giradas |
| Resize | Fit (black edges) in 640×640 | Tamaño con el que se preentrenó YOLO, sin deformar el logo: la imagen de 1920×1080 queda en 640×360 con bandas negras |

**Aumento de datos (Roboflow, solo entrenamiento, ×3):** cada imagen de entrenamiento genera 3 variantes, así que la versión tiene 651 imágenes (573 + 49 + 29). Validación y test se quedan como fotos reales.

| Aumento | Valor | Qué simula |
|---|---|---|
| Crop | Zoom del 0 al 20 % | Lata más cerca o cortada por el borde |
| Rotation | De -10° a +10° | Lata o cámara inclinadas |
| Brightness | De -20 % a +20 % | Habitación más clara u oscura |
| Exposure | De -10 % a +10 % | Ajuste automático de la cámara |
| Blur | Hasta 1 px | Fotograma movido |
| Noise | Hasta el 1 % de los píxeles | Grano de webcam o compresión del stream |

**Aumento de Ultralytics durante el entrenamiento:** YOLO aplica además sus aumentos por defecto en cada época (mosaico, escala, traslación y color), con dos cambios:

| Parámetro | Valor | Motivo |
|---|---|---|
| `fliplr` | 0.0 | El volteo invierte el logo, algo que no ocurre en un vídeo real. La spec deja el flip como experimento |
| `hsv_h` | 0.0 | El color es parte del logo: no se cambia el tono |

### Hiperparámetros

| Parámetro | Valor | Motivo |
|---|---|---|
| `epochs` | 100 | Máximo de vueltas al dataset. Con 573 imágenes cada época dura unos 5 s, así que da margen sin coste |
| `patience` | 20 | Parada anticipada: si la validación no mejora en 20 épocas, se detiene para no sobreajustar |
| `batch` | 16 | Valor estándar de YOLO; cabe en los 15 GB de la T4 |
| `imgsz` | 640 | El mismo tamaño que el dataset |
| `save_period` | 10 | Checkpoint cada 10 épocas, además de `best.pt` y `last.pt` |
| `seed` | 0 | Fija el azar para que el entrenamiento sea reproducible |

### Resultados del entrenamiento

| Dato | Valor |
|---|---|
| Épocas ejecutadas | 81 de 100 (parada anticipada) |
| Mejor época (`best.pt`) | 61 |
| mAP50-95 en validación, época 61 | 0,831 (máximo del entrenamiento) |
| mAP50-95 en validación, época 81 | 0,795 |
| Tiempo total | 424 s (unos 7 minutos) |

**Lectura de las curvas (`results.png`):**

1. **Épocas 1-7:** precision, recall y mAP50 suben hasta casi 1,0. Gracias al preentrenamiento, encontrar los logos le cuesta muy poco.
2. **Épocas 7-61:** el mAP50-95 sube despacio de 0,73 a 0,83. Lo que sigue mejorando es el ajuste de las cajas.
3. **Épocas 61-81:** el error en entrenamiento sigue bajando, pero en validación deja de mejorar (el `val/box_loss` mínimo, 0,694, es también de la época 61). Es el inicio del sobreajuste, y la parada anticipada corta en la época 81.

### Métricas en test

Evaluación de `best.pt` con el conjunto de test (`juntas-1`: 29 imágenes, 58 logos).

| Clase | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| `burn` | 0,996 | 1,000 | 0,995 | 0,776 |
| `monster` | 1,000 | 1,000 | 0,995 | 0,765 |
| **Todas** | **0,998** | **1,000** | **0,995** | **0,770** |

### Limitaciones

Estas métricas son **optimistas** y no prueban que el modelo funcione en streams reales:

- **El test es un solo vídeo:** 29 fotogramas muy parecidos entre sí.
- **Mismo entorno que el entrenamiento:** la misma habitación, mesa, latas y luz.
- **Caso fácil:** en `juntas-1` las dos latas se ven claras y a media distancia.
- **Sin casos lejanos ni con poca luz en test:** los lejanos solo se evalúan en validación (`burn-4-lejos`) y la penumbra no se evalúa (`burn-3-poca-luz` está en entrenamiento).
- **Riesgo de falsos positivos con fuego de videojuegos:** el logo de Burn es una llama. Sin medir todavía.

El mAP50-95 de 0,77 indica que el modelo encuentra los logos, pero las cajas no se ajustan del todo a las etiquetadas.

La matriz de confusión (`confusion_matrix.png`, en la salida de Kaggle) se analiza en la revisión manual del nivel Avanzado.

### Pendiente

- Revisión manual y análisis de fallos con vídeos de referencia (spec §1.11, tareas T-2.5 y T-3.x).
- Negativos con fuego de videojuegos, para medir y reducir los falsos positivos de Burn.
- Modelo v2 con Red Bull.
- Experimento con flip activado (spec §1.8).
