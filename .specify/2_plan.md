# 2. Plan — organización y ejecución

Repo: `background-buzz` · rama de trabajo: `develop` · rama estable: `main`

## 2.1 Principios de trabajo

- **Entender antes de implementar.** Cada tarea empieza identificando los conceptos que implica (técnicas de visión, librerías, patrones). Se implementa cuando están claros.
- **Incrementos pequeños y verificables.** Una tarea, una rama, un PR. Cada tarea termina con un criterio de "hecho" que se puede comprobar.
- **Las decisiones se documentan con su motivo.** Si una elección no se puede justificar, no se toma.
- **El modelo se mejora midiendo, no a ojo.** Cada versión entrenada se evalúa con el mismo conjunto de test y se compara con mAP, precision y recall (spec §1.11).
- **La complejidad entra cuando un nivel la necesita, no antes.**
- **Lo aprendido se anota al momento** en la sección Aprendizajes de `docs/decisiones.md`.

## 2.2 Stack

| Capa | Tecnología |
|---|---|
| Frontend | React · Vite · JavaScript · Tailwind CSS 4 |
| Backend | Python · FastAPI · Pydantic · pydantic-settings · uv |
| Visión | Ultralytics YOLO (entrenamiento, exportación y nivel Esencial) · ONNX Runtime (inferencia desde 🟡) · OpenCV |
| Dataset y entrenamiento | Roboflow · Google Colab |
| Base de datos | PostgreSQL (Docker en local, Supabase en la nube) · SQLAlchemy |
| Calidad | pytest · ruff · pre-commit · gitleaks · GitHub Actions |
| Entorno | Docker · Docker Compose · Git y GitHub |
| Despliegue | Vercel (front) · Render (API) · Supabase (BD y recortes) |
| Gestión | GitHub Issues · GitHub Projects |

Las versiones exactas quedan fijadas en `backend/uv.lock` y `frontend/package-lock.json`.

## 2.3 Estructura del repositorio

Estructura final. Las carpetas y archivos marcados con nivel se crean al llegar a ese nivel, no antes (🟡 medio · 🟠 avanzado · 🔴 experto; sin marca: desde el principio).

```
background-buzz/
├── .specify/                       ← 1_spec.md, 2_plan.md, 3_tasks.md
├── .github/
│   ├── ISSUE_TEMPLATE/tarea.md
│   ├── pull_request_template.md
│   └── workflows/ci.yml
├── backend/
│   ├── app/
│   │   ├── config.py               ← lee el .env (pydantic-settings)
│   │   ├── detector/               ← núcleo de visión
│   │   │   ├── model.py            ← ÚNICO punto de acceso a Ultralytics / ONNX
│   │   │   ├── drawing.py          ← cajas, nombre de la marca y confianza
│   │   │   ├── video.py            (🟡) ← lectura y muestreo de fotogramas
│   │   │   └── crops.py            (🟠) ← recortes de las cajas
│   │   ├── db/                     (🟠)
│   │   │   ├── session.py          ← ÚNICA conexión a la base de datos
│   │   │   ├── models.py           ← tablas (ORM)
│   │   │   ├── crud.py             ← escritura y lectura simple (ORM)
│   │   │   └── reports.py          ← consultas del informe (SQL directo)
│   │   ├── services/               (🟠) ← casos de uso: analizar un vídeo, generar el informe
│   │   ├── storage.py              (🟠) ← ÚNICO punto de acceso al almacenamiento de recortes (disco o Supabase)
│   │   ├── api/                    (🔴)
│   │   │   ├── routes/             ← un archivo por funcionalidad
│   │   │   └── schemas.py          ← contratos de entrada y salida (spec §1.6)
│   │   ├── jobs.py                 (🔴) ← procesamiento en segundo plano
│   │   └── main.py                 (🔴) ← crea la app y registra las rutas
│   ├── scripts/
│   │   ├── detect_image.py
│   │   ├── detect_video.py         (🟡)
│   │   ├── analyze_video.py        (🟠) ← vídeo → base de datos → informe
│   │   └── export_onnx.py          (🟡) ← convierte best.pt en best.onnx
│   ├── tests/
│   ├── models/                     ← pesos del modelo (no se sube)
│   ├── data/                       ← vídeos, salidas y recortes locales (no se sube)
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile                  (🔴)
├── frontend/                       (🔴)
│   ├── src/
│   │   ├── api/client.js           ← ÚNICO punto de llamada al backend
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── index.css               ← Tailwind
│   │   └── App.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── notebooks/
│   └── train_yolo.ipynb            ← entrenamiento y evaluación en Colab
├── docs/
│   ├── arquitectura.png
│   ├── decisiones.md               ← decisiones ampliadas y Aprendizajes
│   └── entrenamiento.md            ← evolución del modelo (v1 → vN) con sus métricas
├── scripts/setup_github.py         ← crea labels, milestones e issues
├── .pre-commit-config.yaml
├── docker-compose.yml              ← en la raíz
├── .env.example
├── .gitignore
├── LICENSE                         ← AGPL-3.0
└── README.md
```

## 2.4 Reglas del backend

- **Capas:** en los niveles 🟢 y 🟡, los scripts llaman directamente a `detector/`. Desde 🟠, los scripts y las rutas llaman a `services/`, y los servicios llaman a `detector/`, `db/` y `storage.py`. Nunca al revés.
- **Rutas finas:** reciben, validan, llaman a un servicio y responden. Sin lógica de negocio.
- **Los servicios no saben de HTTP.** No importan nada de FastAPI. Así los reutilizan los scripts, la API y los tests.
- **`detector/` no sabe de base de datos**, y `db/` no sabe de visión.
- **Solo `detector/model.py` importa `ultralytics` u `onnxruntime`.** Ultralytics va en un grupo de dependencias aparte (`train`) y no entra en la imagen de Docker.
- **El vídeo se analiza de uno en uno** y el archivo subido se borra al terminar (spec §1.10).
- **Análisis interrumpidos:** al arrancar la API, los vídeos que siguen en `processing` pasan a `error` con el mensaje "Análisis interrumpido" (spec §1.10).
- **Solo `storage.py` guarda o lee recortes.** En local usa `CROPS_DIR`; si están las variables de Supabase, usa su almacenamiento.
- **ORM solo en `db/crud.py`; SQL directo solo en `db/reports.py`.** Una única conexión en `db/session.py`.
- **Las tablas se crean al arrancar** con SQLAlchemy (`create_all`). Las migraciones con Alembic quedan fuera de alcance.
- **El SQL de `db/reports.py` es estándar** (`COUNT`, `DISTINCT`, `GROUP BY`…) y funciona igual en PostgreSQL y en SQLite, para que los tests prueben lo mismo que usa la app. El redondeo se hace en Python.
- **Ningún valor de configuración fijo en el código** (umbral de confianza, fotogramas por segundo, límites de archivo, `DATABASE_URL`…). Todo pasa por `config.py`.
- **Los vídeos se validan antes de procesarse** (spec §1.10).
- **Errores controlados:** cada fallo se traduce al código de la spec §1.6 (400, 404, 409, 413, 415, 422) con un mensaje claro.
- **Type hints y docstring breve** en todas las funciones públicas.

## 2.5 Reglas del frontend

- Toda llamada al backend pasa por `src/api/client.js`. Ningún `fetch` suelto en los componentes.
- La URL de la API llega por la variable `VITE_API_URL`.
- Tailwind CSS 4 con el plugin `@tailwindcss/vite`. Sin `tailwind.config.js` ni PostCSS. Si un recurso explica la versión 3, no se sigue.
- **Mobile first:** se diseña para móvil y se amplía con `md:` y `lg:`.
- Componentes pequeños, uno por archivo.
- **Estados visibles:** cargando, procesando, error y vacío en toda acción que llame al backend.
- Accesibilidad básica: `alt` en las imágenes, `label` en los campos y contraste suficiente.
- Modo oscuro: fuera del alcance; es el extra E-3.

## 2.6 Docker y despliegue

| Servicio | Imagen | Puerto | Desde |
|---|---|---|---|
| `db` | PostgreSQL oficial | 5432 | 🟠 |
| `backend` | Python con uv, uvicorn | 8000 | 🔴 |
| `frontend` | Build de Vite servido por nginx:alpine | 5173 → 80 | 🔴 |

- `docker-compose.yml` en la raíz. Lee las variables de `.env`.
- La base de datos usa un volumen para conservar los datos.
- `backend/models/` y `backend/data/` se montan como volúmenes.
- **Objetivo:** con el `.env` relleno, `docker compose up` basta para usar la aplicación en local.

**En la nube (🔴):**
- **Render** construye la API desde `backend/Dockerfile`. Como `models/` no se sube a Git, el `Dockerfile` **descarga `best.onnx` de la GitHub Release** al construir la imagen, usando la variable `MODEL_URL`.
- **Vercel** construye el front desde `frontend/`.
- **Supabase** aloja la base de datos y los recortes.
- CORS de la API limitado a la URL del front en Vercel.

## 2.7 Ramas, commits y PRs

- `main`: solo recibe merges desde `develop` al cerrar cada nivel. Siempre funciona.
- `develop`: integración. Rama por defecto. Nunca se trabaja directamente en ella.
- `main` y `develop` están protegidas: sin borrado, sin force push, solo mediante PR y con el CI en verde. Sin aprobaciones obligatorias, porque el trabajo es individual.
- **Ramas de trabajo**, una por tarea, creadas desde `develop` actualizado y en inglés:
  - `feature/T-x.y-<descripción>` → `feature/T-2.1-video-detection`
  - `fix/T-x.y-<descripción>` → `fix/T-3.4-percentage-rounding`
  - `docs/T-x.y-<descripción>` → `docs/T-1.6-readme-setup`
  - `chore/T-x.y-<descripción>` → `chore/T-0.3-pre-commit`
- **Commits convencionales**, un commit por idea, con el formato `tipo(ámbito): verbo en infinitivo + descripción`. Prefijo en inglés y mensaje en español:
  - `feat(detector): detectar logos en vídeo`
  - `test(db): comprobar el cálculo del porcentaje por marca`
  - `docs(specs): añadir extra E-4, exportar informe a PDF`
- **Prefijos:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.
- **Ámbitos:** `specs`, `detector`, `db`, `services`, `api`, `frontend`, `notebook`, `docker`, `ci`, `readme`.
- **PRs:**
  - Título: commit convencional + ID de la tarea → `feat(detector): detectar logos en vídeo (T-2.1)`.
  - Descripción con la plantilla: `## Qué hace` → `Closes #N` → `## Cómo probarlo` → `## Checklist`.
  - Checklist: las casillas fijas de la plantilla + el "Hecho" de la tarea (de `3_tasks.md`) + las reglas de este plan que apliquen. Se indica de dónde sale cada casilla y solo se marca `[x]` lo comprobado.
  - Método de merge: siempre **Create a merge commit**.
- **Al cerrar una tarea:** merge → `git switch develop` → `git pull` → `git branch -d <rama>`.
- **Tags** al cerrar cada nivel: `v1-esencial`, `v2-medio`, `v3-avanzado`, `v4-experto`, y `v1.0` en la entrega.
- **Idiomas:** código, nombres de archivos, ramas y columnas del tablero en inglés. Commits, issues, PRs, documentación e interfaz en español.

### Plantilla de PR

```markdown
## Qué hace
<!-- Resumen breve del cambio -->

Closes #N

## Cómo probarlo
<!-- Pasos para comprobarlo -->

## Checklist
<!-- Fijas de la plantilla -->
- [ ] Funciona en local
- [ ] Tests y linter en verde
- [ ] Sin secretos en el código
- [ ] Documentación o aprendizajes actualizados si la tarea lo requería
<!-- "Hecho" de la tarea (3_tasks.md) -->
<!-- Reglas de 2_plan.md que apliquen -->
```

## 2.8 Issues, labels, milestones y tablero

- Una issue por tarea de `3_tasks.md`, titulada con su ID: `T-2.1 · Detección en vídeo`.
- La issue no repite el diseño: enlaza a la sección de la spec. Si la issue y la spec no coinciden, manda la spec.
- Los extras se numeran (`E-1`, `E-2`…), se registran primero en la spec §1.13 y después se abre su issue con la label `extras`.
- **Labels:**
  - Fase: `fase:0-arranque`, `fase:1-esencial`, `fase:2-medio`, `fase:3-avanzado`, `fase:4-experto`, `fase:5-entrega`, `extras`.
  - Tipo: `nivel:esencial|medio|avanzado|experto`, `nivel:mejora`, `nivel:seguridad`, `nivel:soporte`.
  - `gate` para los hitos bloqueantes.
- **Milestones**, uno por fase, con fecha límite:

| Milestone | Fecha límite |
|---|---|
| Arranque | mar 27 oct |
| Nivel Esencial | mié 28 oct |
| Nivel Medio | jue 29 oct |
| Nivel Avanzado | sáb 31 oct |
| Nivel Experto | dom 1 nov, 20:00 (código congelado) |
| Entrega | mar 3 nov (exposición: mié 4 nov) |
| Extras | sin fecha |

- **Tablero** (GitHub Projects): Backlog · To Do · In Progress · In Review · Done, con la descripción de cada columna en español. Cada día se mueven a To Do las tareas previstas.
- Labels, milestones e issues se crean con `scripts/setup_github.py`, que lee `3_tasks.md`. Así las issues no pueden desincronizarse de las tareas. Se puede ejecutar varias veces: no duplica lo que ya existe.

## 2.9 Calidad

- **Tests (pytest):** usan un **detector falso**, sin cargar YOLO ni conectarse a la red. Rápidos, gratuitos y deterministas. Cubren las reglas del informe (spec §1.7), la validación de archivos (§1.10), el guardado en base de datos (con SQLite) y las rutas de la API (🔴).
- **Tests del pre y postprocesado de ONNX** (🟡): con datos inventados y sin modelo real, comprueban la conversión de coordenadas al tamaño original de la imagen, el filtro por umbral y la eliminación de cajas repetidas (spec R-12).
- **Linter (ruff)** en el backend.
- **pre-commit:** gitleaks (bloquea cualquier commit con un secreto) y ruff (revisa y formatea).
- **CI (GitHub Actions)** en cada PR: `ruff` + `pytest` en el backend; `npm run lint` y `npm run build` en el frontend (🔴). Insignia en el README.
- **Evaluación del modelo:** cada versión entrenada se evalúa en el notebook con el mismo conjunto de test (mAP50, mAP50-95, precision y recall por marca). Los resultados se anotan en `docs/entrenamiento.md` para comparar versiones.

## 2.10 Documentación

Se escribe al cerrar cada nivel, no al final.

| Documento | Contenido |
|---|---|
| `README.md` | Qué es y para quién, captura o GIF, diagrama, cómo arrancarlo con Docker, uso de los scripts y de la API, stack, estructura, model card (datos, métricas, limitaciones), próximos pasos y licencia |
| `docs/decisiones.md` | Decisiones ampliadas y sección Aprendizajes |
| `docs/entrenamiento.md` | Evolución del modelo (v1 → vN): dataset, aumento de datos, parámetros y métricas de cada versión |

## 2.11 Definición de "hecho" (válida para toda tarea)

- Cumple el criterio "Hecho" de la tarea.
- Funciona en local.
- Sin secretos en el código.
- Tests y linter en verde.
- PR fusionado en `develop` e issue cerrada.
- Documentación o aprendizajes actualizados si la tarea lo requería.

## 2.12 Seguridad y datos

- Los secretos solo van en `.env`, que nunca se sube; `.env.example` con valores vacíos.
- Nunca se pegan claves en el chat.
- `.gitignore` incluye `.env`, `backend/data/`, `backend/models/` y los archivos de vídeo.
- El dataset vive en Roboflow; los pesos entrenados se guardan en Google Drive y el modelo final se publica como asset de la release.
