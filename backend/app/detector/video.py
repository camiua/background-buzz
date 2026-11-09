"""Lectura y muestreo de los fotogramas de un vídeo (spec §1.7)."""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class VideoInfo:
    """Datos básicos de un vídeo."""

    fps: float
    frame_count: int
    width: int
    height: int


def sampling_step(fps: float, sample_fps: float) -> int:
    """Cada cuántos fotogramas se analiza uno: round(fps / sample_fps), mínimo 1."""
    return max(1, round(fps / sample_fps))


def real_sample_fps(fps: float, step: int) -> float:
    """Fotogramas analizados por segundo de vídeo con ese salto."""
    return fps / step


def read_info(path: Path) -> VideoInfo:
    """Devuelve los fps, el número de fotogramas y el tamaño de un vídeo."""
    capture = _open(path)
    try:
        return VideoInfo(
            fps=capture.get(cv2.CAP_PROP_FPS),
            frame_count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
            width=int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
    finally:
        capture.release()


def read_frames(path: Path) -> Iterator[tuple[int, np.ndarray]]:
    """Recorre el vídeo y devuelve cada fotograma con su número, empezando en 0."""
    capture = _open(path)
    try:
        index = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            yield index, frame
            index += 1
    finally:
        capture.release()


def _open(path: Path) -> cv2.VideoCapture:
    """Abre un vídeo o lanza un error claro si no se puede leer."""
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"No se puede abrir el vídeo: {path}")
    return capture
