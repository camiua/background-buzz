"""Único punto de acceso al modelo de detección (spec D-8)."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ultralytics import YOLO


@dataclass(frozen=True)
class Detection:
    """Un logo detectado en una imagen."""

    brand: str
    confidence: float
    box: tuple[int, int, int, int]  # x1, y1, x2, y2 en píxeles de la imagen original


class Detector:
    """Detecta logos de marcas con un modelo YOLO."""

    def __init__(self, model_path: Path, confidence_threshold: float) -> None:
        if not model_path.exists():
            raise FileNotFoundError(f"No se encuentra el modelo: {model_path}")
        self._model = YOLO(str(model_path))
        self._confidence_threshold = confidence_threshold

    def detect(self, image: np.ndarray) -> list[Detection]:
        """Devuelve los logos detectados en una imagen BGR (formato de OpenCV)."""
        result = self._model.predict(
            image, conf=self._confidence_threshold, verbose=False
        )[0]
        detections = []
        for box, class_id, confidence in zip(
            result.boxes.xyxy.tolist(),
            result.boxes.cls.tolist(),
            result.boxes.conf.tolist(),
            strict=True,
        ):
            x1, y1, x2, y2 = (round(value) for value in box)
            detections.append(
                Detection(
                    brand=result.names[int(class_id)],
                    confidence=confidence,
                    box=(x1, y1, x2, y2),
                )
            )
        return detections
