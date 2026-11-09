"""Tests de la lectura y el muestreo de vídeo (spec §1.7, T-2.1)."""

from pathlib import Path

import cv2
import numpy as np
import pytest

from app.detector.video import read_frames, read_info, real_sample_fps, sampling_step


def make_video(path: Path, fps: float, frames: int) -> Path:
    """Crea un vídeo sintético de color liso, para no depender de archivos reales."""
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (64, 48))
    for i in range(frames):
        writer.write(np.full((48, 64, 3), i % 256, dtype=np.uint8))
    writer.release()
    return path


@pytest.mark.parametrize(
    ("fps", "expected_step", "expected_sample_fps"),
    [(30, 6, 5.0), (25, 5, 5.0), (24, 5, 4.8)],
)
def test_sampling_step_and_real_fps(fps, expected_step, expected_sample_fps):
    step = sampling_step(fps, sample_fps=5)
    assert step == expected_step
    assert real_sample_fps(fps, step) == pytest.approx(expected_sample_fps)


def test_sampling_step_is_at_least_one():
    assert sampling_step(fps=3, sample_fps=5) == 1


@pytest.mark.parametrize("fps", [30, 25, 24])
def test_read_info_and_frames(tmp_path, fps):
    video = make_video(tmp_path / f"sintetico_{fps}.avi", fps=fps, frames=fps * 2)

    info = read_info(video)
    frames = list(read_frames(video))

    assert info.fps == pytest.approx(fps)
    assert (info.width, info.height) == (64, 48)
    assert len(frames) == fps * 2
    assert [index for index, _ in frames] == list(range(fps * 2))


def test_open_missing_video_raises(tmp_path):
    with pytest.raises(ValueError, match="No se puede abrir"):
        read_info(tmp_path / "no_existe.mp4")
