# 3. Tasks

Cada tarea se convierte en una issue de GitHub con el mismo ID en el título. **Hecho** = criterio verificable, no "creo que funciona". **Conceptos** = lo que hay que tener claro antes de implementar la tarea.

Leyenda: 🟢 Esencial · 🟡 Medio · 🟠 Avanzado · 🔴 Experto · ⭐ Mejora de producto · 🔐 Seguridad · ⚪ Soporte

## Fase 0 — Arranque (mar 27 – mié 28)

Las issues se crean justo después de las specs, para que todo el trabajo posterior tenga su issue. Las tareas se hacen en el orden de su número.

**T-0.1 · Repositorio, ramas y protección** ⚪
Repo público `background-buzz` con README, `.gitignore` de Python y licencia AGPL-3.0 (spec D-18). Rama `develop` por defecto. Ruleset sobre `main` y `develop`: sin borrado, sin force push y PR obligatorio sin aprobaciones. El CI obligatorio se añade en T-0.7.
Conceptos: ramas, rama por defecto, protección de ramas, licencias de código abierto.
Hecho: `git branch -a` muestra `main` y `develop` en remoto, y `develop` es la rama por defecto.

**T-0.2 · Specs iniciales** ⚪ · dep: T-0.1
`.specify/` con `1_spec.md`, `2_plan.md` y `3_tasks.md`.
Conceptos: desarrollo guiado por especificaciones, flujo rama → PR → merge.
Hecho: primer PR fusionado en `develop` con las tres specs.

**T-0.3 · Plantillas de issue y PR** ⚪ · dep: T-0.2
`.github/ISSUE_TEMPLATE/tarea.md` y `.github/pull_request_template.md` (plan §2.7).
Conceptos: plantillas de GitHub, trazabilidad entre issue y PR.
Hecho: al crear una issue o un PR en GitHub, aparece la plantilla.

**T-0.4 · Labels, milestones, issues y tablero** ⚪ · dep: T-0.3
`scripts/setup_github.py` adaptado desde IdeaLab: crea labels y milestones con fecha (plan §2.8) y una issue por tarea leyendo este archivo, sin duplicar las existentes. Tablero en GitHub Projects con cinco columnas.
Conceptos: automatización con scripts, GitHub CLI, idempotencia.
Hecho: todas las tareas tienen su issue, con labels y milestone, y aparecen en el tablero.

**T-0.5 · Estructura base y configuración** ⚪ · dep: T-0.4
`.gitignore` ampliado (Python, Node, `.env`, `.venv`, `node_modules`, `backend/data/`, `backend/models/`, `*.mp4`, `*.mov`, `*.avi`). `.gitattributes` con `* text=auto eol=lf`, para que los archivos de texto usen siempre saltos de línea de Linux (LF), también en Windows. `.env.example` con todas las variables de la spec §1.9, sin valores. `backend/` con `uv init`, `pyproject.toml` (configuración de ruff y pytest, grupo de dependencias `train` para Ultralytics) y `uv.lock`.
Conceptos: `.gitignore`, `.gitattributes` y saltos de línea (LF y CRLF), variables de entorno, secretos, gestión de dependencias con uv y lockfile.
Hecho: `git status` no muestra nunca `.env` aunque exista, `git ls-files --eol` muestra `i/lf` en todos los archivos de texto y `uv run ruff check .` se ejecuta sin errores.

**T-0.6 · pre-commit: secretos y estilo** 🔐 · dep: T-0.5
`.pre-commit-config.yaml` con gitleaks y ruff (revisión y formato).
Conceptos: hooks de Git, pre-commit, linter y formateador.
Hecho: un commit con una clave falsa de prueba queda bloqueado, y un archivo Python mal formateado se corrige solo al hacer commit.

**T-0.7 · Integración continua** ⚪ · dep: T-0.6
`.github/workflows/ci.yml`: ruff y pytest con uv en cada PR. El CI pasa a ser obligatorio en el ruleset de `main` y `develop`. Insignia en el README.
Conceptos: CI, workflows de GitHub Actions, status checks.
Hecho: un PR muestra las comprobaciones en verde, y no se puede fusionar si fallan.

**T-0.8 · Entorno local y cuentas** ⚪
uv, Node LTS y Docker Desktop instalados. Cuentas de Roboflow y Google (Colab y Drive). Las cuentas de Supabase, Render y Vercel se crean en T-4.5.
Hecho: `uv --version`, `node --version` y `docker run hello-world` funcionan, y se abre un notebook de Colab con GPU.

## Fase 1 — Nivel Esencial (jue 29)

**T-1.1 · Sesión de fotos** 🟢 · jue 29
Latas de Red Bull, Monster (varias variantes) y Burn, más imágenes negativas, según la spec §1.8 (composición y variedad). Capturas de streams si se encuentran (R-6). Se adelanta al martes porque el etiquetado depende de ella.
Conceptos: variedad de datos, parecido entre datos de entrenamiento y de uso real, imágenes negativas.
Hecho: al menos 100 imágenes por marca y 50 negativas, con todas las situaciones de variedad cubiertas en cada marca.

**T-1.2 · Etiquetado, reparto y aumento en Roboflow** 🟢 · dep: T-1.1
Etiquetado con la guía de la spec §1.8. Reparto 70/20/10 agrupado por sesión o vídeo. Preprocesado y aumento de datos (flip desactivado). Exportación en formato YOLO como dataset v1.
Conceptos: bounding box, formato YOLO, entrenamiento/validación/test, fuga de datos entre conjuntos, aumento de datos.
Hecho: dataset v1 exportado con el conjunto de test fijado, y `docs/entrenamiento.md` registra el número de imágenes por marca y conjunto, el preprocesado y el aumento aplicados.

**T-1.3 · Primer entrenamiento en Colab** 🟢 · dep: T-1.2
`notebooks/train_yolo.ipynb`: YOLO nano preentrenado, transfer learning con el dataset v1, pesos guardados en Drive y evaluación sobre el conjunto de test.
Conceptos: transfer learning, épocas, sobreajuste, mAP, precision, recall.
Hecho: `best.pt` está en Drive, y las métricas del test por marca (modelo v1) están en `docs/entrenamiento.md`.

**T-1.4 · Detección en imagen** 🟢 · dep: T-1.3
`config.py` con pydantic-settings, `detector/model.py` con Ultralytics, `detector/drawing.py` (caja y nombre de la marca) y `scripts/detect_image.py` (spec §1.5).
Conceptos: inferencia, umbral de confianza, eliminación de cajas repetidas (NMS), dibujo con OpenCV.
Hecho: con una imagen del conjunto de test, el script genera una imagen con la caja sobre el logo, y ningún otro módulo importa `ultralytics`.

**T-1.5 · Documentación del nivel** 🟢 · dep: T-1.4
README (qué es, para quién, cómo instalar con uv y cómo usar `detect_image.py`), docstrings y una captura en `docs/img/`. Primeros apuntes en Aprendizajes.
Hecho: alguien que no conoce el proyecto puede ejecutar `detect_image.py` siguiendo el README.

**T-1.GATE · Nivel Esencial** 🟢 · jue 29 · dep: T-1.1 a T-1.5
Hecho: gate de la spec §1.2 cumplido, PR `develop` → `main` fusionado, tag `v1-esencial` y release con `best.pt` como asset.

## Fase 2 — Nivel Medio (vie 30)

**T-2.1 · Lectura y muestreo de vídeo** 🟡 · dep: T-1.GATE
`detector/video.py` con OpenCV: salto entre fotogramas y frecuencia real según la spec §1.7. Tests con un vídeo sintético generado dentro del propio test.
Conceptos: fotogramas, fps, muestreo, generadores de Python.
Hecho: los tests comprueban el salto y la frecuencia real con vídeos de 30, 25 y 24 fps.

**T-2.2 · Exportación a ONNX** 🟡 · dep: T-1.GATE
`scripts/export_onnx.py` convierte `best.pt` en `best.onnx`.
Conceptos: ONNX como formato de intercambio, exportación de modelos.
Hecho: `best.onnx` se genera y se carga con ONNX Runtime.

**T-2.3 · Inferencia con ONNX Runtime** 🟡 · dep: T-2.2
`detector/model.py` pasa a ONNX (spec D-7 y D-8): redimensionado con bandas (letterbox), normalización, inferencia, decodificación de la salida, umbral y eliminación de cajas repetidas con OpenCV. Tests del pre y postprocesado con datos inventados (plan §2.9). Comparación con Ultralytics (R-12).
Conceptos: letterbox, tensores y su forma (NCHW), salida de YOLO, IoU, NMS.
Hecho: tests en verde, y en las imágenes de test las cajas de ONNX coinciden con las de Ultralytics (misma marca e IoU ≥ 0,9). El resultado se anota en Aprendizajes.

**T-2.4 · Vídeo de salida con detecciones** 🟡 · dep: T-2.1, T-2.3
`scripts/detect_video.py`: vídeo de salida con la caja y el nombre de la marca debajo de cada detección. El vídeo conserva todos los fotogramas; cada uno muestra las detecciones del último fotograma analizado.
Conceptos: escritura de vídeo con OpenCV, códecs.
Hecho: con un vídeo de prueba se genera un `.mp4` que se reproduce con las cajas y los nombres.

**T-2.5 · Vídeos de referencia** 🟡
Dos vídeos de 20-60 s con varias marcas (grabados o fragmentos de streams). Se anotan a mano los intervalos en los que aparece cada marca (spec §1.11).
Conceptos: verdad de referencia (ground truth), anotación manual.
Hecho: los dos vídeos tienen sus intervalos anotados y su porcentaje real por marca calculado en `docs/entrenamiento.md`.

**T-2.6 · Documentación del nivel** 🟡 · dep: T-2.4
README (uso de `detect_video.py` y exportación a ONNX) y Aprendizajes (ONNX y pre/postprocesado).
Hecho: el README explica cómo generar un vídeo con detecciones desde cero.

**T-2.GATE · Nivel Medio** 🟡 · vie 30 · dep: T-2.1 a T-2.6
Hecho: gate de la spec §1.2 cumplido, PR `develop` → `main` fusionado, tag `v2-medio` y release con `best.onnx` como asset.

## Fase 3 — Nivel Avanzado (sáb 31)

**T-3.1 · Confianza en pantalla** 🟠 · sáb 31
`detector/drawing.py` muestra la marca y la confianza (por ejemplo, `monster 87%`).
Hecho: el vídeo de salida muestra nombre y porcentaje en cada detección.

**T-3.2 · PostgreSQL y tablas** 🟠 · sáb 31
Servicio `db` en `docker-compose.yml` con volumen. `db/session.py` y `db/models.py` (spec §1.4). Tablas creadas al arrancar con `create_all`.
Conceptos: ORM, sesión, claves primaria y foránea, volúmenes de Docker.
Hecho: con `docker compose up db`, al arrancar se crean las dos tablas y se ven con `psql`.

**T-3.3 · Guardado de detecciones y recortes** 🟠 · sáb 31 · dep: T-3.2
`db/crud.py`, `detector/crops.py` y `storage.py` (en disco). Tests con SQLite.
Conceptos: CRUD, transacciones, recortes con slicing de NumPy, punto único de acceso al almacenamiento.
Hecho: tests en verde y, tras un análisis de prueba, las detecciones están en la base de datos y cada `crop_path` apunta a un recorte que existe.

**T-3.4 · Informe** 🟠 · sáb 31 · dep: T-3.3
`db/reports.py` con SQL estándar y redondeo en Python (plan §2.4), según las reglas de la spec §1.7.
Conceptos: `GROUP BY`, `COUNT(DISTINCT)`, agregación.
Hecho: tests en verde para cada regla de la spec §1.7: varias latas de la misma marca en un fotograma cuentan una vez, los porcentajes pueden sumar más de 100 y una marca ausente no aparece.

**T-3.5 · Análisis completo** 🟠 · sáb 31 · dep: T-2.4, T-3.4
`services/analysis.py` y `scripts/analyze_video.py` (spec §1.5). Desde aquí, los scripts pasan por `services/` (plan §2.4).
Conceptos: capa de servicios, orquestación.
Hecho: con un vídeo de referencia, el script guarda detecciones y recortes e imprime el informe por marca.

**T-3.6 · Evaluación** 🟠 · sáb 31 · dep: T-2.5, T-3.5
Spec §1.11: ajuste del umbral con un vídeo de referencia y comprobación con el otro, error del informe, tiempo de análisis con nano y con small. Si hace falta y hay tiempo, modelo v2 con más datos.
Conceptos: error absoluto, ajuste de umbral, sobreajuste a los datos de validación.
Hecho: la tabla de la spec §1.11 está rellena en `docs/entrenamiento.md`, y P-1 y P-2 están resueltas en la spec.

**T-3.7 · Model card y documentación** 🟠 · sáb 31 · dep: T-3.6
Model card en el README (datos, métricas y limitaciones), uso de `analyze_video.py` y Aprendizajes.
Hecho: la model card refleja las métricas reales de T-3.6, incluidas las que no alcanzan el objetivo.

**T-3.GATE · Nivel Avanzado** 🟠 · sáb 31 · dep: T-3.1 a T-3.7
Hecho: gate de la spec §1.2 cumplido, PR `develop` → `main` fusionado y tag `v3-avanzado`.

## Fase 4 — Nivel Experto (dom 1, hasta las 20:00)

**T-4.1 · API** 🔴 · dom 1
`main.py`, `api/schemas.py` y `api/routes/` con las cuatro rutas de la spec §1.6. Validación de archivos (§1.10), errores controlados y CORS. Tests de las rutas con el detector falso.
Conceptos: subida de archivos (multipart), códigos de estado HTTP, Pydantic, `TestClient`, inyección de dependencias.
Hecho: tests de rutas en verde y, desde `/docs`, un vídeo se sube correctamente y unos archivos de prueba devuelven 413 y 415.

**T-4.2 · Procesamiento en segundo plano** 🔴 · dom 1 · dep: T-4.1
`jobs.py`: un vídeo cada vez, avance en `progress`, borrado del vídeo al terminar y análisis interrumpidos al arrancar (spec §1.10).
Conceptos: tareas en segundo plano, cola, estados de un trabajo.
Hecho: al subir dos vídeos seguidos, el segundo queda `pending` hasta que termina el primero, y el vídeo subido ya no existe en disco al acabar.

**T-4.3 · Docker del backend** 🔴 · dom 1 · dep: T-4.2
`backend/Dockerfile` con uv, sin el grupo `train`, que descarga `best.onnx` con `MODEL_URL`. `docker-compose.yml` completo (plan §2.6).
Conceptos: imagen, capas, argumentos de construcción, compose.
Hecho: desde un clon limpio, `docker compose up` deja la API funcionando y `/api/health` responde `"model_loaded": true`.

**T-4.4 · Front** 🔴 · dom 1 · dep: T-4.1
Vite + React + Tailwind 4. `src/api/client.js`, subida del vídeo, estado con consultas periódicas y tabla del informe. Estados visibles y mobile first (plan §2.5). ESLint y build añadidos al CI.
Conceptos: componentes, props, `useState`, `useEffect`, consultas periódicas (polling), `FormData`.
Hecho: desde la web se sube un vídeo, se ve el avance y aparece el informe; en vista móvil todo se ve en una columna; el CI del front está en verde.

**T-4.5 · Despliegue** 🔴 · dom 1, opcional · dep: T-4.3, T-4.4
Opcional desde el reajuste del 28 de octubre (ver plan de recorte). Supabase (base de datos y bucket de recortes, `storage.py` con Supabase), Render (API desde el `Dockerfile`) y Vercel (front con `VITE_API_URL`). CORS limitado al front. Se comprueban las condiciones de los planes gratuitos (R-9).
Conceptos: variables de entorno en producción, CORS, arranque en frío.
Hecho: gate de la spec §1.2 Experto cumplido desde la URL pública.

**T-4.GATE · Nivel Experto y código congelado** 🔴 · dom 1, 20:00 · dep: T-4.1 a T-4.4 (y T-4.5 si se completa)
Hecho: gate de la spec §1.2 Experto cumplido, PR `develop` → `main` fusionado y tag `v4-experto`. A partir de aquí solo se corrigen errores.

## Fase 5 — Entrega y exposición (dom 1 – mié 4)

**T-5.1 · README final** · dom 1 (noche)
Captura o GIF, diagrama, insignia del CI, instalación con Docker, URL pública (si se completa T-4.5), stack, estructura y próximos pasos.

**T-5.2 · Decisiones, aprendizajes y cobertura** · lun 2
`docs/decisiones.md` completo y los IDs de tarea añadidos a la cobertura del briefing (spec §1.12).

**T-5.3 · Vídeo de la demo** · lun 2
Demo grabada de principio a fin, como plan B (R-10).

**T-5.4 · Presentación técnica** · lun 2
Problema (con los estudios) → solución → arquitectura → dataset y entrenamiento (v1 → vN) → demo → evaluación (spec §1.11) → decisiones → aprendizajes → próximos pasos.

**T-5.5 · Cierre del repositorio** · lun 2
Tablero sin tareas en curso, `main` actualizada y tag `v1.0`.

**T-5.6 · Entrega** · mar 3

**T-5.7 · Ensayo y plan B** · mar 3
Dos ensayos cronometrados. Demo en local preparada, vídeo de la demo listo, servicio de Render despertado antes de empezar (si hay despliegue) y prueba de compartir pantalla.

**T-5.8 · Exposición** · mié 4

## Extras (después de la entrega, o antes si hay margen)

**E-1 · Gráfica de línea de tiempo** ⭐ — en qué segundos aparece cada marca.
**E-2 · Exportar el informe a CSV** ⭐ — para trabajar los datos en una hoja de cálculo.
**E-3 · Modo oscuro** ⭐ — variante por clase, activable con un botón y respetando la preferencia del sistema.

## Calendario

| Día | Trabajo | Cierre |
|---|---|---|
| mar 27 – mié 28 | Fase 0 completa | |
| jue 29 | Fase 1: T-1.1 a T-1.5 (si no da tiempo, el entrenamiento de T-1.3 queda en marcha por la noche y T-1.4 pasa al viernes por la mañana) | `v1-esencial` |
| vie 30 | Fase 2 | `v2-medio` |
| sáb 31 | Fase 3: T-3.1 a T-3.7 | `v3-avanzado` |
| dom 1 | T-4.1 a T-4.4 · T-4.5 si hay margen · código congelado a las 20:00 · T-5.1 | `v4-experto` |
| lun 2 | T-5.2 a T-5.5 | `v1.0` |
| mar 3 | Entrega · ensayo y plan B | |
| mié 4 | Exposición | |

## Plan de recorte

Si hay retraso, se recorta en este orden:

1. Extras pendientes.
2. Modelo v2 en T-3.6: se documenta el v1 con sus limitaciones.
3. T-4.5 (despliegue): API y front se presentan funcionando en local con Docker.
4. T-4.4 reducido: solo subida del vídeo y tabla del informe, sin más diseño.

No se recortan: los gates hasta el nivel Avanzado, la guía de etiquetado y el conjunto de test fijo, los tests de las reglas del informe, la evaluación de la spec §1.11, el código congelado, el vídeo de la demo ni el ensayo.

### Reajuste del 28 de octubre

La Fase 0 terminó el miércoles 28 en lugar del martes 27, y las latas para el dataset se consiguen el jueves 29. Se aplica el plan de recorte así:

- El nivel Esencial pasa al jueves 29 y el Medio al viernes 30. El Avanzado se comprime en el sábado 31 y mantiene su fecha.
- **Punto 3 aplicado de forma preventiva:** el despliegue (T-4.5) pasa a ser opcional. El nivel Experto se compromete en local con Docker; si el domingo hay margen, se despliega.
- El código congelado, la entrega y la exposición no cambian.

Al congelar el código no entra ninguna funcionalidad nueva. Lo que no esté terminado el domingo a las 20:00 se presenta sin ello.
