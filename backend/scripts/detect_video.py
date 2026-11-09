"""Detecta logos en un vídeo y genera una copia con las cajas (spec §1.5 y §1.7).

Uso, desde backend/:
    uv run python -m scripts.detect_video data/video.mp4
    uv run python -m scripts.detect_video data/video.mp4 --output data/salida.mp4
"""

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

import cv2

from app.config import BACKEND_DIR, settings
from app.detector.drawing import draw_detections
from app.detector.model import Detection, Detector
from app.detector.video import read_frames, read_info, real_sample_fps, sampling_step


def main() -> None:
    """Analiza un fotograma de cada `step` y guarda el vídeo con las cajas."""
    parser = argparse.ArgumentParser(description="Detecta logos en un vídeo.")
    parser.add_argument("video", type=Path, help="vídeo de entrada")
    parser.add_argument(
        "--output",
        type=Path,
        help="vídeo de salida (por defecto, data/outputs/<nombre>_detecciones.mp4)",
    )
    args = parser.parse_args()

    try:
        info = read_info(args.video)
    except ValueError as error:
        sys.exit(str(error))

    step = sampling_step(info.fps, settings.sample_fps)
    sample_fps = real_sample_fps(info.fps, step)
    print(
        f"{info.frame_count} fotogramas a {info.fps:.1f} fps: se analiza 1 de cada "
        f"{step} ({sample_fps:.1f} por segundo)"
    )

    output = args.output or (
        BACKEND_DIR / "data" / "outputs" / f"{args.video.stem}_detecciones.mp4"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    detector = Detector(settings.model_file, settings.confidence_threshold)
    writer = None
    detections: list[Detection] = []
    analyzed = 0
    frames_per_brand: Counter[str] = Counter()
    start = time.perf_counter()

    for index, frame in read_frames(args.video):
        if writer is None:
            # El tamaño se toma del primer fotograma: en los vídeos del móvil
            # puede no coincidir con el de los metadatos si el vídeo va girado.
            height, width = frame.shape[:2]
            writer = cv2.VideoWriter(
                str(output), cv2.VideoWriter_fourcc(*"mp4v"), info.fps, (width, height)
            )
        if index % step == 0:
            detections = detector.detect(frame)
            analyzed += 1
            frames_per_brand.update({d.brand for d in detections})
        # Cada fotograma muestra las detecciones del último fotograma analizado.
        writer.write(draw_detections(frame, detections))

    if writer is None:
        sys.exit(f"El vídeo no tiene fotogramas: {args.video}")
    writer.release()

    print(f"Analizados {analyzed} fotogramas en {time.perf_counter() - start:.0f} s.")
    for brand, frames in frames_per_brand.most_common():
        print(
            f"{brand:>8}  {frames / sample_fps:.1f} s  "
            f"({frames / analyzed:.0%} de los fotogramas analizados)"
        )
    if not frames_per_brand:
        print("No se ha detectado ningún logo.")
    print(f"Vídeo guardado en {output}")


if __name__ == "__main__":
    main()
