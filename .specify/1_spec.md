# 1. Spec — Background Buzz

> *Revealing energy drink ads in gaming streams*

Fuente de verdad del diseño. Si algo de aquí cambia, se actualiza este archivo antes de tocar código. El progreso vive en GitHub Issues y en el tablero, no aquí.

## 1.1 Objetivo

Las bebidas energéticas son uno de los productos con más presencia en el contenido de gaming y streaming, cuyo público es mayoritariamente joven. Las organizaciones de salud y los observatorios de consumo que quieren medir esa exposición tienen que revisar horas de vídeo a mano. Background Buzz es una prueba de concepto que analiza vídeos de streams, detecta los logos de bebidas energéticas con un modelo de visión por computador y genera un informe con cuánto tiempo y qué porcentaje del vídeo aparece cada marca, guardando cada detección en una base de datos.

Restricción principal: coste cero. Solo se usan servicios en plan gratuito (Google Colab, Roboflow, Supabase, Render y Vercel), aceptando sus límites de memoria, velocidad y uso.

Alcance comprometido: los cuatro niveles del briefing (Esencial, Medio, Avanzado y Experto), con el Avanzado como objetivo seguro. Desde el reajuste del 28 de octubre (plan de recorte en `3_tasks.md`), el Experto se compromete en local y el despliegue en la nube es opcional. Trabajo individual. Código congelado: domingo 1 de noviembre, 20:00. Entrega: martes 3 de noviembre. Exposición: miércoles 4 de noviembre (online, por confirmar).

**Ámbito:** marcas comercializadas en España, analizadas en vídeos de streamers de habla hispana.
**Marcas (clases del modelo):** `redbull`, `monster`, `burn`.

## 1.2 Alcance por niveles

Cada nivel se cierra con un **gate** (criterio comprobable) y un **tag** de Git, así que siempre existe una versión entregable. La versión entregada se marca con el tag `v1.0`.

| Nivel | Qué añade | Gate | Tag | Milestone |
|---|---|---|---|---|
| 🟢 Esencial | Modelo YOLO preentrenado reentrenado con dataset propio; detecta al menos una marca en una imagen y dibuja su caja. Repo con ramas y commits limpios, código documentado y README | Con una imagen que no estaba en el entrenamiento, el modelo dibuja la caja sobre el logo | `v1-esencial` | jue 29 oct |
| 🟡 Medio | Procesa archivos de vídeo; muestra el nombre de la marca debajo de cada detección | Con un vídeo de prueba, se genera un vídeo de salida con las cajas y el nombre de la marca | `v2-medio` | vie 30 oct |
| 🟠 Avanzado | Confianza visible junto al nombre; modelo multimarca (tres marcas); base de datos con detecciones y recortes; informe de tiempo y porcentaje (§1.7); model card en el README | Con un vídeo con varias marcas, se guardan detecciones y recortes, se genera el informe y las métricas de §1.11 están medidas y documentadas | `v3-avanzado` | sáb 31 oct |
| 🔴 Experto | API con procesamiento en segundo plano y validación de archivos; front web responsive; despliegue en Vercel, Render y Supabase | Desde el front se sube un vídeo corto y se obtiene el informe: en local con Docker como compromiso, y desde la URL pública si se completa el despliegue (opcional desde el reajuste del 28 oct) | `v4-experto` | dom 1 nov, 20:00 |

## 1.3 Decisiones de arquitectura

| # | Decisión | Motivo |
|---|---|---|
| D-1 | YOLO (Ultralytics), versión nano o small | Detector de una sola pasada, diseñado para tiempo real; las versiones ligeras funcionan en CPU. |
| D-2 | Transfer learning sobre un modelo preentrenado, con dataset propio | Con unas 100-150 imágenes por marca es suficiente. El briefing pide reentrenar un modelo preentrenado con imágenes obtenidas por los propios expertos. |
| D-3 | Roboflow para etiquetar, aumentar datos y exportar | Etiquetado asistido y aumento de datos sin código; exporta en formato YOLO. |
| D-4 | Entrenamiento en Google Colab | El portátil no tiene GPU NVIDIA; Colab ofrece GPU gratuita. Los pesos se guardan en Google Drive por si se corta la sesión. |
| D-5 | Inferencia en CPU | El briefing no exige tiempo real; un modelo ligero es suficiente en el portátil y en Render. |
| D-6 | Muestreo de unos 5 fotogramas por segundo | Reduce el tiempo de análisis en CPU y es suficiente para medir el tiempo de aparición. |
| D-7 | Inferencia con ONNX Runtime desde el nivel Medio, en local y en la nube. Ultralytics solo se usa para entrenar, exportar a ONNX y en el nivel Esencial | Un solo camino de código, igual en local y en Render. Elimina PyTorch de la imagen de Docker y reduce la memoria necesaria. |
| D-8 | Un único punto de acceso al modelo (`detector/model.py`): preprocesado, inferencia y postprocesado (umbral y eliminación de cajas repetidas con OpenCV) | Cambiar de modelo o de versión de YOLO es tocar un archivo. Ningún otro módulo importa Ultralytics ni ONNX Runtime. |
| D-9 | Backend en Python con FastAPI | El modelo y OpenCV están en Python. FastAPI valida con Pydantic y genera la documentación de la API en `/docs`. |
| D-10 | Frontend en React (Vite + JavaScript + Tailwind CSS 4), separado del backend, en lugar de Streamlit o Gradio | El nivel Experto exige una API: con React + FastAPI, la API sirve al front y a cualquier otro cliente. JavaScript para centrarse en los conceptos de React; Tailwind para un diseño responsive rápido. |
| D-11 | PostgreSQL: en Docker para desarrollar y en Supabase en la nube | El mismo motor en los dos entornos. Supabase aloja la base de datos y los recortes, accesibles desde la API desplegada. |
| D-12 | SQLAlchemy (ORM) para tablas y escritura; SQL directo para el informe | El ORM aporta seguridad y portabilidad (PostgreSQL en la app, SQLite en los tests); el SQL directo hace más claras las consultas de agregación. |
| D-13 | Procesamiento de vídeos en segundo plano, de uno en uno | Analizar un vídeo tarda: la API responde al momento con un identificador y el front consulta el estado, sin conexiones que se cortan. Uno cada vez para no agotar la memoria de Render. |
| D-14 | Docker para la base de datos, el backend y el frontend | Con el `.env` relleno, `docker compose up` basta para usar la aplicación en local. Como la inferencia es ONNX en todas partes (D-7), la misma imagen del backend se despliega en Render. |
| D-15 | Despliegue: Vercel (front) y Render (API) | Planes gratuitos; Vercel está pensado para fronts estáticos y Render acepta imágenes Docker. |
| D-16 | Dependencias con uv y lockfile | El entorno local, Docker y el CI usan exactamente las mismas versiones. |
| D-17 | Secretos solo en `.env`, con detector de secretos antes de cada commit | El repositorio es público. `.env.example` documenta las variables sin valores. |
| D-18 | Licencia AGPL-3.0 | Ultralytics YOLO usa AGPL-3.0; el repositorio es público y de código abierto. |

## 1.4 Contrato A — Datos

**Tabla `videos`**

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero, PK | Identificador |
| `filename` | texto | Nombre del vídeo |
| `duration_s` | decimal | Duración en segundos |
| `fps` | decimal | Fotogramas por segundo del vídeo original |
| `sample_fps` | decimal | Fotogramas analizados por segundo |
| `frames_analyzed` | entero | Total de fotogramas analizados |
| `status` | texto | `pending`, `processing`, `done`, `error` |
| `progress` | entero | Avance del análisis, de 0 a 100 |
| `error_message` | texto, opcional | Motivo del error, si lo hay |
| `created_at` | fecha y hora | Momento de subida |

**Tabla `detections`**

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero, PK | Identificador |
| `video_id` | entero, FK → `videos.id` | Vídeo al que pertenece |
| `frame_number` | entero | Número de fotograma |
| `timestamp_s` | decimal | Segundo del vídeo |
| `brand` | texto | `redbull`, `monster` o `burn` |
| `confidence` | decimal (0-1) | Confianza de la detección |
| `x1`, `y1`, `x2`, `y2` | entero | Coordenadas de la caja |
| `crop_path` | texto | Ruta (local) o URL (Supabase) del recorte |

## 1.5 Contrato B — Scripts (niveles 🟢 🟡 🟠)

Antes del nivel Experto, el sistema se usa desde la línea de comandos. Los scripts llaman al mismo código que después usa la API.

| Script | Nivel | Entrada | Salida |
|---|---|---|---|
| `scripts/detect_image.py` | 🟢 | Ruta de una imagen | Imagen con las cajas dibujadas |
| `scripts/detect_video.py` | 🟡 | Ruta de un vídeo | Vídeo con las cajas y el nombre de la marca (y la confianza desde 🟠) |
| `scripts/analyze_video.py` | 🟠 | Ruta de un vídeo | Detecciones y recortes guardados en la base de datos, e informe por marca en la terminal |

Ejemplo:
```bash
uv run python scripts/analyze_video.py data/videos/stream1.mp4
```

## 1.6 Contrato C — API (nivel 🔴)

Base en local: `http://localhost:8000`. Documentación interactiva en `/docs`. Todas las respuestas en JSON.

| Método y ruta | Qué hace | Respuesta correcta |
|---|---|---|
| `GET /api/health` | Estado del servicio, del modelo y de la base de datos | `200` |
| `POST /api/videos` | Sube un vídeo (multipart, campo `file`) y lanza el análisis en segundo plano | `202` |
| `GET /api/videos/{id}` | Estado y avance del análisis | `200` |
| `GET /api/videos/{id}/report` | Informe por marca (§1.7) | `200` |

**`GET /api/health`**
```json
{ "status": "ok", "model_loaded": true, "database": true }
```

**`POST /api/videos`**
```json
{ "video_id": 1, "status": "pending" }
```

**`GET /api/videos/{id}`**
```json
{ "video_id": 1, "filename": "stream1.mp4", "status": "processing", "progress": 40, "error_message": null }
```

**`GET /api/videos/{id}/report`**
```json
{
  "video_id": 1,
  "filename": "stream1.mp4",
  "duration_s": 20.0,
  "confidence_threshold": 0.5,
  "brands": [
    { "brand": "monster", "seconds": 5.0, "percentage": 25.0 },
    { "brand": "redbull", "seconds": 2.4, "percentage": 12.0 }
  ]
}
```
Las marcas que no aparecen no se incluyen en `brands`. Si no aparece ninguna, `brands` es una lista vacía.

**Errores**

| Código | Cuándo | Cuerpo |
|---|---|---|
| `400` | El vídeo no se puede leer o supera la duración máxima | `{ "detail": "El vídeo dura más de 30 segundos." }` |
| `404` | El vídeo no existe | `{ "detail": "Vídeo no encontrado." }` |
| `409` | Se pide el informe antes de terminar el análisis | `{ "detail": "El análisis aún no ha terminado.", "status": "processing" }` |
| `413` | El archivo supera el tamaño máximo | `{ "detail": "El archivo supera los 50 MB." }` |
| `415` | El formato no está admitido | `{ "detail": "Formato no admitido. Usa .mp4, .mov o .avi." }` |
| `422` | Datos de entrada no válidos | Formato estándar de FastAPI |

Nunca se devuelve al usuario el texto de una excepción interna.

## 1.7 Contrato D — Reglas del informe

| Regla | Definición |
|---|---|
| Fotogramas analizados | Los muestreados según D-6 |
| Salto entre fotogramas | `step = round(fps ÷ SAMPLE_FPS)`, como mínimo 1: se analiza uno de cada `step` fotogramas |
| Frecuencia real | `sample_fps = fps ÷ step`. Es la que se guarda en la base de datos y se usa en los cálculos, aunque no coincida exactamente con `SAMPLE_FPS` |
| Aparición | Una marca **aparece** en un fotograma si hay al menos una detección suya con confianza ≥ umbral |
| Varias latas | Varias detecciones de la misma marca en un fotograma cuentan como **un** fotograma |
| Umbral de confianza | 0,50 al empezar; configurable (§1.9) y ajustado según §1.11 |
| Tiempo de una marca | Fotogramas con la marca ÷ `sample_fps` |
| Porcentaje de una marca | Fotogramas con la marca ÷ `frames_analyzed` × 100 |
| Suma de porcentajes | Puede superar el 100 %, porque varias marcas pueden aparecer en el mismo fotograma |
| Redondeo | Segundos y porcentajes con un decimal, aplicado en Python |

## 1.8 Contrato E — Dataset, etiquetado y preprocesado

**Composición**

| Elemento | Requisito |
|---|---|
| Origen | Imágenes propias, como pide el briefing: fotos de la autora y capturas de vídeos de streams |
| Mínimo por marca | 100 imágenes originales con el logo (antes del aumento de datos) |
| Imágenes negativas | Al menos 50 sin ningún logo de las tres marcas (escritorios, setups, streams, otras bebidas), para reducir falsos positivos |
| Variedad en cada marca | Lata en la mano · en la mesa o el escritorio · lejos y pequeña · poca luz o luz de pantalla · parcialmente tapada · junto a otras marcas |
| Monster | Varias variantes de color de lata |
| Capturas de streams reales | Las que se encuentren (ver R-6) |

**Guía de etiquetado**

| Situación | Regla |
|---|---|
| Qué se etiqueta | **Solo el logo**, no la lata entera |
| Qué es el logo | El emblema de la marca: su símbolo y su nombre cuando aparecen juntos formando una unidad |
| Ajuste de la caja | Ajustada al logo visible, sin margen extra |
| Varios logos | Una caja por cada logo visible (dos latas de la misma marca = dos cajas) |
| Logo parcialmente tapado | Se etiqueta si la marca se reconoce; si no, no |
| Otras marcas | No se etiquetan |
| Coherencia | Las mismas reglas en todas las sesiones de etiquetado |

**Preprocesado, reparto y aumento de datos**

| Paso | Decisión | Motivo |
|---|---|---|
| Orientación | Automática | Las fotos del móvil pueden venir giradas |
| Redimensionado | 640 × 640 manteniendo la proporción | Tamaño de entrada estándar de YOLO |
| Normalización | Píxeles a 0-1, aplicada por YOLO en entrenamiento e inferencia | La red trabaja con valores en la misma escala |
| Reparto | 70 % entrenamiento · 20 % validación · 10 % test | Entrenar, ajustar y evaluar con datos distintos |
| Agrupación | Las imágenes de una misma sesión o de un mismo vídeo van al mismo conjunto | Evitar casi-copias del entrenamiento en el test |
| Conjunto de test | Se fija con la primera versión y no se cambia | Comparar versiones del modelo de forma justa |
| Aumento de datos | Solo en entrenamiento: rotación ligera, recorte, brillo, exposición, desenfoque y ruido | Variedad de condiciones sin hacer más fotos |
| Flip horizontal | Desactivado por defecto; se prueba como experimento y se documenta en `docs/entrenamiento.md` | Invierte el texto de los logos, algo que no ocurre en vídeos reales |

## 1.9 Contrato F — Configuración (.env)

| Variable | Ejemplo | Nivel |
|---|---|---|
| `MODEL_PATH` | `models/best.onnx` (en el nivel Esencial: `models/best.pt`) | 🟢 |
| `CONFIDENCE_THRESHOLD` | `0.5` | 🟢 |
| `SAMPLE_FPS` | `5` | 🟡 |
| `DATABASE_URL` | `postgresql://…@localhost:5432/background_buzz` (secreto) | 🟠 |
| `CROPS_DIR` | `data/crops` | 🟠 |
| `MODEL_URL` | URL de `best.onnx` en la GitHub Release (la usa el `Dockerfile` al construir la imagen) | 🔴 |
| `MAX_UPLOAD_MB` | `50` | 🔴 |
| `MAX_DURATION_S` | `30` | 🔴 |
| `CORS_ORIGINS` | `http://localhost:5173` | 🔴 |
| `SUPABASE_URL` | `https://<proyecto>.supabase.co` | 🔴 |
| `SUPABASE_KEY` | (secreto) | 🔴 |
| `SUPABASE_BUCKET` | `crops` | 🔴 |
| `VITE_API_URL` | `http://localhost:8000` (en el `.env` del front) | 🔴 |

En local, los recortes se guardan en `CROPS_DIR`. Si están definidas las variables de Supabase, se suben a su almacenamiento.

## 1.10 Contrato G — Archivos, datos y seguridad

| Tema | Regla |
|---|---|
| Formatos de vídeo | `.mp4`, `.mov`, `.avi` |
| Límites en la nube | 30 segundos y 50 MB |
| Límites en local | Configurables (§1.9) |
| Secretos | Solo en `.env`, que nunca se sube; `.env.example` con valores vacíos |
| Archivos pesados | Dataset en Roboflow; vídeos fuera de Git; modelo entrenado como asset de una GitHub Release |
| Vídeos de terceros | Fragmentos de streams públicos, solo con fines académicos y sin redistribuirlos |
| Recortes | Solo la zona de la caja detectada |
| Vídeos subidos | Se borran al terminar el análisis, también si falla. Solo se conservan las detecciones y los recortes |
| Concurrencia | Se analiza un vídeo cada vez; los demás esperan con estado `pending` |
| Análisis interrumpidos | Si la API se reinicia a mitad de un análisis, al arrancar ese vídeo pasa a `error` con el mensaje "Análisis interrumpido" |
| CORS | La API solo acepta peticiones de los orígenes de `CORS_ORIGINS` |

## 1.11 Evaluación y objetivos orientativos

Los objetivos son **orientativos**: se revisan con los datos del primer entrenamiento (P-1) y, si no se alcanzan, se documenta por qué en la model card.

| Qué se evalúa | Cómo | Objetivo orientativo |
|---|---|---|
| Modelo | mAP50, mAP50-95, precision y recall por marca sobre el conjunto de test | mAP50 global ≥ 0,70 |
| Informe | 2 vídeos de referencia (20-60 s) con los intervalos de cada marca anotados a mano; se compara el porcentaje del informe con el real | Error ≤ 10 puntos porcentuales por marca |
| Rendimiento | Tiempo de análisis en el portátil (CPU) con el muestreo de D-6 | Vídeo de 30 s en ≤ 2 minutos |

- El umbral de confianza se ajusta con uno de los vídeos de referencia y se comprueba con el otro.
- La comparación de rendimiento decide entre YOLO nano y small (P-2).

## 1.12 Cobertura del briefing

| Requisito o criterio | Dónde se cumple |
|---|---|
| Entrenar un modelo con una nueva categoría y bounding box visible | §1.2 Esencial · D-1 · D-2 |
| Reconocer al menos una marca | §1.2 Esencial |
| Repositorio con ramas organizadas y commits limpios | `2_plan.md` §2.7 |
| Documentación del código y README | `2_plan.md` §2.10 |
| Funcionar con archivos de vídeo | §1.2 Medio · §1.5 · D-6 |
| Nombre de la clase debajo de cada detección | §1.2 Medio |
| Porcentaje de seguridad visible | §1.2 Avanzado |
| Base de datos con nombre del vídeo, recortes y otros datos | §1.4 · §1.2 Avanzado |
| Modelo multimarca | §1.2 Avanzado · §1.8 |
| Informe de tiempo y porcentaje de aparición | §1.7 · §1.11 |
| Front para subir vídeos y ver resultados | §1.2 Experto · D-10 |
| Modelo servido en la nube y apificado | §1.6 · D-7 · D-15 |
| **Evaluación:** preprocesado (resizing, normalización, escalado) | §1.8 |
| **Evaluación:** datasets de imágenes para detección | §1.8 · D-3 |
| **Evaluación:** reentrenar un modelo preentrenado | D-2 |
| **Evaluación:** detección en tiempo real | D-1: YOLO es un detector de una sola pasada diseñado para tiempo real; aquí se aplica sobre vídeos grabados, como permite el briefing |
| **Evaluación:** aumento de datos (flip, crop, color jitter) | §1.8 (el flip se evalúa como experimento) |
| **Entrega:** repositorio documentado | `2_plan.md` §2.10 |
| **Entrega:** demo en vivo | Demo en local, con vídeo grabado de respaldo |
| **Entrega:** presentación técnica | `3_tasks.md`, fase de entrega |
| **Entrega:** tablero Kanban | `2_plan.md` §2.8 |
| **Tecnología recomendada:** Streamlit o Gradio | Sustituido por React (D-10) |

Los IDs de tarea se añaden a esta tabla al cerrar `3_tasks.md`.

## 1.13 Fuera de alcance

| Elemento | Motivo |
|---|---|
| Tracking y recuento de latas | El briefing pide tiempo, no recuento. Mejora futura |
| Otros países y marcas | Prueba de concepto; el briefing prevé ampliar después |
| Usuarios, registro e inicio de sesión | No aportan al objetivo de la demo |
| Detección en directo con webcam | El caso de uso es analizar vídeos grabados |
| App móvil | Los usuarios trabajan en ordenador; se cubre con web responsive |
| Análisis por enlace de YouTube u otras plataformas | Puede chocar con sus condiciones de uso; se suben archivos |
| TypeScript en el front | Mejora futura |

**Extras (issues con la label `extras`, si hay tiempo):**
- E-1 · Gráfica de línea de tiempo por marca.
- E-2 · Exportar el informe a CSV.
- E-3 · Modo oscuro en el front.

## 1.14 Riesgos

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R-1 | Poco tiempo (6 días hasta la congelación, trabajo individual) | Alto | Cada nivel termina con una versión completa y etiquetada; plan de recorte en `3_tasks.md`, aplicado el 28 oct (despliegue opcional); el Avanzado es el objetivo seguro |
| R-2 | Crear y etiquetar el dataset lleva más de lo previsto | Alto | Empezar el primer día; tres marcas; etiquetado asistido |
| R-3 | Límites o cortes de la GPU gratuita de Colab | Medio | Guardar pesos y checkpoints en Google Drive |
| R-4 | Logos pequeños, tapados o con mala luz en los streams | Medio | Fotos tipo stream, capturas reales y aumento de datos; limitaciones documentadas en la model card |
| R-5 | Confusión entre variantes de color de Monster | Medio | Fotografiar varias variantes |
| R-6 | Poca presencia de estas marcas en streams españoles | Medio | Comprobarlo antes de cerrar el dataset; vídeos grabados por la autora para la demo |
| R-7 | RAM y CPU limitadas del plan gratuito de Render | Alto | Modelo nano en ONNX, vídeos cortos y procesamiento en segundo plano |
| R-8 | Arranque en frío de Render (~1 min) | Bajo | Despertar el servicio antes de la exposición; demo principal en local |
| R-9 | Cambios en los planes gratuitos de los servicios | Medio | Verificar las condiciones al configurar cada servicio |
| R-10 | Falla la conexión durante la exposición online | Medio | Vídeo de la demo grabado; demo en local sin depender de la nube |
| R-11 | Documentación de Tailwind 3 mezclada con la 4 | Bajo | Seguir solo documentación de Tailwind 4 |
| R-12 | El preprocesado y el postprocesado de ONNX se programan a mano (D-8) y pueden no coincidir con los de Ultralytics | Medio | Comparar las cajas de ONNX con las de Ultralytics sobre las mismas imágenes de test antes de cerrar el nivel Medio; usar la eliminación de cajas repetidas de OpenCV |

## 1.15 Decisiones pendientes

| # | Decisión | Cuándo se decide |
|---|---|---|
| P-1 | Confirmar o ajustar los objetivos orientativos de §1.11 | Tras el primer entrenamiento |
| P-2 | Versión de YOLO: nano o small | Tras comparar la velocidad en CPU |
| P-3 | Exposición presencial u online | Cuando se confirme |
