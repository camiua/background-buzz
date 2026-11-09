"""Dibujo de las detecciones sobre una imagen (plan §2.4: cajas legibles)."""

import cv2
import numpy as np

from app.detector.model import Detection

# Un color fijo por marca, en BGR (el orden de canales de OpenCV).
BRAND_COLORS: dict[str, tuple[int, int, int]] = {
    "burn": (0, 90, 230),  # naranja
    "monster": (40, 160, 0),  # verde
    "redbull": (150, 60, 10),  # azul
}
DEFAULT_COLOR = (128, 128, 128)  # gris, para una marca sin color asignado
TEXT_COLOR = (255, 255, 255)  # blanco
FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_detections(image: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Devuelve una copia de la imagen con la caja y el nombre de cada marca."""
    output = image.copy()
    # El grosor y el texto crecen con la imagen, para que se lean en fotos grandes.
    scale = max(output.shape[:2]) / 1000
    line = max(2, round(3 * scale))
    font_scale = max(0.5, 0.8 * scale)
    text_line = max(1, round(2 * scale))
    padding = max(3, round(6 * scale))

    for detection in detections:
        color = BRAND_COLORS.get(detection.brand, DEFAULT_COLOR)
        x1, y1, x2, y2 = detection.box
        cv2.rectangle(output, (x1, y1), (x2, y2), color, line)

        (text_w, text_h), baseline = cv2.getTextSize(
            detection.brand, FONT, font_scale, text_line
        )
        label_h = text_h + baseline + 2 * padding
        # La etiqueta va debajo de la caja; si no cabe, sube dentro de la caja.
        top = y2 if y2 + label_h <= output.shape[0] else y2 - label_h
        cv2.rectangle(
            output,
            (x1, top),
            (x1 + text_w + 2 * padding, top + label_h),
            color,
            cv2.FILLED,
        )
        cv2.putText(
            output,
            detection.brand,
            (x1 + padding, top + padding + text_h),
            FONT,
            font_scale,
            TEXT_COLOR,
            text_line,
            cv2.LINE_AA,
        )
    return output
