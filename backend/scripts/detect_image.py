"""Detecta logos en una imagen y guarda una copia con las cajas (spec §1.5).

Uso, desde backend/:
    uv run python -m scripts.detect_image data/foto.jpg
    uv run python -m scripts.detect_image data/foto.jpg --output data/salida.jpg
"""

import argparse
import sys
from pathlib import Path

import cv2

from app.config import BACKEND_DIR, settings
from app.detector.drawing import draw_detections
from app.detector.model import Detector


def main() -> None:
    """Lee la imagen, detecta los logos y guarda la imagen con las cajas."""
    parser = argparse.ArgumentParser(description="Detecta logos en una imagen.")
    parser.add_argument("image", type=Path, help="imagen de entrada")
    parser.add_argument(
        "--output",
        type=Path,
        help="imagen de salida (por defecto, data/outputs/<nombre>_detecciones.jpg)",
    )
    args = parser.parse_args()

    image = cv2.imread(str(args.image))
    if image is None:
        sys.exit(f"No se puede leer la imagen: {args.image}")

    detector = Detector(settings.model_file, settings.confidence_threshold)
    detections = detector.detect(image)
    for detection in detections:
        print(f"{detection.brand:>8}  {detection.confidence:.2f}  {detection.box}")
    if not detections:
        print("No se ha detectado ningún logo.")

    output = args.output or (
        BACKEND_DIR / "data" / "outputs" / f"{args.image.stem}_detecciones.jpg"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), draw_detections(image, detections))
    print(f"Imagen guardada en {output}")


if __name__ == "__main__":
    main()
