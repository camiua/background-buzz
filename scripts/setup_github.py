"""Crea en GitHub las labels, los milestones y las issues del proyecto.

Lee las tareas de `.specify/3_tasks.md` y crea lo que falte siguiendo el plan
(§2.8). Es idempotente: si se ejecuta varias veces, no duplica nada.

Uso (desde la raíz del repo):
    python scripts/setup_github.py --dry-run      # muestra lo que haría
    python scripts/setup_github.py                # lo crea de verdad
    python scripts/setup_github.py --project 1    # y añade las issues al tablero 1

Requisitos: GitHub CLI (`gh`) con sesión iniciada y los permisos `repo` y
`project` (este último solo para `--project`).
"""

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

TASKS_FILE = Path(__file__).resolve().parent.parent / ".specify" / "3_tasks.md"

# Labels del plan §2.8: nombre -> (color, descripción).
LABELS: dict[str, tuple[str, str]] = {
    "fase:0-arranque": ("c5def5", "Fase 0: arranque del repositorio"),
    "fase:1-esencial": ("c5def5", "Fase 1: nivel Esencial"),
    "fase:2-medio": ("c5def5", "Fase 2: nivel Medio"),
    "fase:3-avanzado": ("c5def5", "Fase 3: nivel Avanzado"),
    "fase:4-experto": ("c5def5", "Fase 4: nivel Experto"),
    "fase:5-entrega": ("c5def5", "Fase 5: entrega y exposición"),
    "extras": ("d4c5f9", "Idea fuera de la spec, registrada en §1.13"),
    "nivel:esencial": ("2ea44f", "Requisito del nivel Esencial"),
    "nivel:medio": ("fbca04", "Requisito del nivel Medio"),
    "nivel:avanzado": ("d93f0b", "Requisito del nivel Avanzado"),
    "nivel:experto": ("b60205", "Requisito del nivel Experto"),
    "nivel:mejora": ("5319e7", "Mejora de producto"),
    "nivel:seguridad": ("0052cc", "Seguridad"),
    "nivel:soporte": ("bfbfbf", "Soporte: repositorio, entorno y herramientas"),
    "gate": ("1d1d1d", "Hito bloqueante que cierra un nivel"),
}

PHASE_LABELS: dict[str, str] = {
    "0": "fase:0-arranque",
    "1": "fase:1-esencial",
    "2": "fase:2-medio",
    "3": "fase:3-avanzado",
    "4": "fase:4-experto",
    "5": "fase:5-entrega",
    "extras": "extras",
}

# Clave de fase -> (título del milestone, fecha límite o None).
# GitHub solo guarda el día; se usa el mediodía UTC para que la fecha no se
# desplace un día según la zona horaria. La hora exacta vive en el plan.
MILESTONES: dict[str, tuple[str, str | None]] = {
    "0": ("Arranque", "2026-10-27T12:00:00Z"),
    "1": ("Nivel Esencial", "2026-10-28T12:00:00Z"),
    "2": ("Nivel Medio", "2026-10-29T12:00:00Z"),
    "3": ("Nivel Avanzado", "2026-10-31T12:00:00Z"),
    "4": ("Nivel Experto", "2026-11-01T12:00:00Z"),
    "5": ("Entrega", "2026-11-03T12:00:00Z"),
    "extras": ("Extras", None),
}

EMOJI_LABELS: dict[str, str] = {
    "🟢": "nivel:esencial",
    "🟡": "nivel:medio",
    "🟠": "nivel:avanzado",
    "🔴": "nivel:experto",
    "⭐": "nivel:mejora",
    "🔐": "nivel:seguridad",
    "⚪": "nivel:soporte",
}

PHASE_RE = re.compile(r"^## Fase (\d+) —")
EXTRAS_RE = re.compile(r"^## Extras")
TASK_RE = re.compile(
    r"^\*\*(?P<id>T-\d+\.(?:\d+|GATE)|E-\d+) · (?P<title>[^*]+)\*\*(?P<rest>.*)$"
)


@dataclass
class Task:
    """Una tarea de 3_tasks.md."""

    id: str
    title: str
    phase: str
    emojis: list[str] = field(default_factory=list)
    when: str = ""
    deps: str = ""
    description: list[str] = field(default_factory=list)
    concepts: str = ""
    done: str = ""

    @property
    def issue_title(self) -> str:
        """Título de la issue: `T-1.1 · Sesión de fotos`."""
        return f"{self.id} · {self.title}"

    @property
    def labels(self) -> list[str]:
        """Labels de fase, de nivel y, si corresponde, `gate`."""
        labels = [PHASE_LABELS[self.phase]]
        labels += [EMOJI_LABELS[e] for e in self.emojis]
        if self.id.endswith("GATE"):
            labels.append("gate")
        return labels

    @property
    def milestone(self) -> str:
        """Título del milestone de su fase."""
        return MILESTONES[self.phase][0]


def parse_tasks(text: str) -> list[Task]:
    """Extrae las tareas de 3_tasks.md.

    Una tarea empieza en una línea `**ID · Título** …` y termina en la primera
    línea en blanco o en la siguiente tarea. Solo se leen las secciones
    `## Fase N` y `## Extras`; el resto (calendario, plan de recorte) se ignora.
    """
    tasks: list[Task] = []
    phase: str | None = None
    current: Task | None = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("## "):
            current = None
            if match := PHASE_RE.match(line):
                phase = match.group(1)
            elif EXTRAS_RE.match(line):
                phase = "extras"
            else:
                phase = None
            continue

        if phase is None:
            continue

        if match := TASK_RE.match(line):
            current = Task(id=match["id"], title=match["title"].strip(), phase=phase)
            rest = match["rest"]
            if " — " in rest:  # Extras: "⭐ — descripción"
                rest, description = rest.split(" — ", 1)
                current.description.append(description.strip())
            for part in (p.strip() for p in rest.split("·")):
                if not part:
                    continue
                if part.startswith("dep:"):
                    current.deps = part.removeprefix("dep:").strip()
                elif part in EMOJI_LABELS:
                    current.emojis.append(part)
                else:
                    current.when = part
            tasks.append(current)
            continue

        if current is None or not line:
            current = None
            continue

        if line.startswith("Conceptos:"):
            current.concepts = line.removeprefix("Conceptos:").strip()
        elif line.startswith("Hecho:"):
            current.done = line.removeprefix("Hecho:").strip()
        else:
            current.description.append(line)

    return tasks


def issue_body(task: Task, tasks_url: str) -> str:
    """Cuerpo de la issue, con la estructura de la plantilla `tarea.md`."""
    description = "\n".join(task.description) or task.title
    when = f"\n\n**Cuándo:** {task.when}" if task.when else ""
    return (
        "## Qué hay que hacer\n"
        f"{description}{when}\n\n"
        f"**Spec:** [`3_tasks.md`]({tasks_url}) · `{task.id}` y las secciones "
        "de la spec citadas arriba.\n\n"
        "## Conceptos\n"
        f"{task.concepts or '—'}\n\n"
        "## Hecho\n"
        f"- [ ] {task.done or 'Ver «Qué hay que hacer».'}\n\n"
        "## Dependencias\n"
        f"{task.deps or 'Ninguna'}\n"
    )


def gh(*args: str, stdin: str | None = None) -> str:
    """Ejecuta un comando de GitHub CLI y devuelve su salida.

    Si el comando falla, muestra el error de `gh` y termina el script.
    """
    result = subprocess.run(
        ["gh", *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        sys.exit(f"Error al ejecutar gh {' '.join(args[:3])}…\n{result.stderr}")
    return result.stdout.strip()


def ensure_labels(dry_run: bool) -> None:
    """Crea las labels del plan que aún no existen."""
    existing = {
        label["name"]
        for label in json.loads(gh("label", "list", "--limit", "200", "--json", "name"))
    }
    for name, (color, description) in LABELS.items():
        if name in existing:
            print(f"  = label {name} (ya existe)")
            continue
        print(f"  + label {name}")
        if not dry_run:
            gh("label", "create", name, "--color", color, "--description", description)


def ensure_milestones(repo: str, dry_run: bool) -> None:
    """Crea los milestones del plan que aún no existen."""
    existing = {
        m["title"]
        for m in json.loads(
            gh("api", f"repos/{repo}/milestones?state=all&per_page=100")
        )
    }
    for title, due_on in MILESTONES.values():
        if title in existing:
            print(f"  = milestone {title} (ya existe)")
            continue
        print(f"  + milestone {title} ({due_on[:10] if due_on else 'sin fecha'})")
        if not dry_run:
            fields = ["-f", f"title={title}"]
            if due_on:
                fields += ["-f", f"due_on={due_on}"]
            gh("api", f"repos/{repo}/milestones", "--method", "POST", *fields)


def ensure_issues(
    tasks: list[Task], repo: str, project: int | None, dry_run: bool
) -> None:
    """Crea una issue por tarea si no existe y, opcionalmente, la añade al tablero.

    Una issue existe si su título empieza por el ID de la tarea seguido de ` · `.
    """
    issues = json.loads(
        gh("issue", "list", "--state", "all", "--limit", "500", "--json", "title,url")
    )
    existing = {issue["title"].split(" · ")[0]: issue["url"] for issue in issues}
    tasks_url = f"https://github.com/{repo}/blob/develop/.specify/3_tasks.md"
    owner = repo.split("/")[0]

    in_project: set[str] = set()
    if project is not None:
        items = json.loads(
            gh(
                "project",
                "item-list",
                str(project),
                "--owner",
                owner,
                "--limit",
                "500",
                "--format",
                "json",
            )
        )["items"]
        in_project = {item["content"].get("url", "") for item in items}

    for task in tasks:
        url = existing.get(task.id)
        if url:
            print(f"  = {task.issue_title} (ya existe)")
        else:
            print(
                f"  + {task.issue_title}  [{', '.join(task.labels)}] → {task.milestone}"
            )
            if dry_run:
                if project is not None:
                    print(f"    → al tablero {project}")
                continue
            label_args = [arg for label in task.labels for arg in ("--label", label)]
            url = gh(
                "issue",
                "create",
                "--title",
                task.issue_title,
                "--body-file",
                "-",
                "--milestone",
                task.milestone,
                *label_args,
                stdin=issue_body(task, tasks_url),
            )
            time.sleep(1)  # Pausa para no superar el límite de creación de GitHub.

        if project is not None and url not in in_project:
            print(f"    → al tablero {project}")
            if not dry_run:
                gh("project", "item-add", str(project), "--owner", owner, "--url", url)


def main() -> None:
    """Punto de entrada: lee las tareas y sincroniza GitHub."""
    # Emojis y tildes en la terminal de Windows.
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Crea labels, milestones e issues desde 3_tasks.md."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="muestra lo que haría sin crear nada"
    )
    parser.add_argument(
        "--project", type=int, help="número del tablero de GitHub Projects"
    )
    args = parser.parse_args()

    tasks = parse_tasks(TASKS_FILE.read_text(encoding="utf-8"))
    repo = gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")

    mode = "MODO PRUEBA: no se crea nada" if args.dry_run else "Creando en GitHub"
    print(f"{mode} · {repo} · {len(tasks)} tareas leídas de {TASKS_FILE.name}\n")

    print("Labels")
    ensure_labels(args.dry_run)
    print("\nMilestones")
    ensure_milestones(repo, args.dry_run)
    print("\nIssues")
    ensure_issues(tasks, repo, args.project, args.dry_run)
    print("\nListo.")


if __name__ == "__main__":
    main()
