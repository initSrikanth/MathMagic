"""Free, offline media readiness check. Never calls HeyGen or changes a lesson.

Build a NON-PRODUCTION 1080p transport fixture from four seconds of the approved
720p composite. This preserves framing but does not claim native 1080p detail,
new narration alignment, or a working independent-avatar compositor.
"""
import argparse
import hashlib
import io
import json
import struct
import subprocess
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "videos/MathMagic_Mixed_Numbers_FINAL.mp4"
SOURCE_HASH = "92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56"


def run(*args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format",
                          "-of", "json", str(path)))


def frame(path, seconds):
    return Image.open(io.BytesIO(run("ffmpeg", "-v", "error", "-ss", str(seconds),
                                    "-i", str(path), "-frames:v", "1", "-f",
                                    "image2pipe", "-vcodec", "png", "-"))).convert("RGB")


def top_level_atoms(path):
    atoms = []
    with path.open("rb") as stream:
        while header := stream.read(8):
            size, kind = struct.unpack(">I4s", header)
            header_size = 8
            if size == 1:
                size = struct.unpack(">Q", stream.read(8))[0]
                header_size = 16
            atoms.append(kind.decode("ascii"))
            if size == 0:
                break
            assert size >= header_size
            stream.seek(size - header_size, 1)
    return atoms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True,
                        help="Scratch output directory outside the repository")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    assert ROOT not in evidence.parents, "Keep generated evidence outside the repository"
    evidence.mkdir(parents=True, exist_ok=True)
    assert digest(SOURCE) == SOURCE_HASH, "Approved source bytes changed"
    # Exact arithmetic independently validates the approved worked examples.
    assert Fraction(7, 4) == 1 + Fraction(3, 4)
    assert Fraction(11, 4) == 2 + Fraction(3, 4)
    assert 3 + Fraction(2, 5) == Fraction(17, 5)
    assert 2 + Fraction(1, 2) > 2 + Fraction(1, 4)
    assert Fraction(9, 4) == 2 + Fraction(1, 4)
    # Exercise installed graphics libraries with horizontal fraction notation.
    graphic = Image.new("RGB", (1920, 1080), "white")
    drawing = ImageDraw.Draw(graphic)
    drawing.text((920, 400), "7", fill="#17334d", font_size=72)
    drawing.line((900, 490, 980, 490), fill="#17334d", width=6)
    drawing.text((920, 510), "4", fill="#17334d", font_size=72)
    graphic.save(evidence / "programmatic-fraction.png")
    if args.build:
        args.fixture.parent.mkdir(parents=True, exist_ok=True)
        run("ffmpeg", "-v", "error", "-y", "-i", str(SOURCE), "-t", "4",
            "-vf", "scale=1920:1080:flags=lanczos,fps=24,setsar=1",
            "-map", "0:v:0", "-map", "0:a:0", "-c:v", "libx264",
            "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(args.fixture))
    info = probe(args.fixture)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert (video["width"], video["height"], video["codec_name"], video["pix_fmt"]) == (
        1920, 1080, "h264", "yuv420p")
    assert audio["codec_name"] == "aac"
    assert 3.9 <= float(info["format"]["duration"]) <= 4.1
    atoms = top_level_atoms(args.fixture)
    assert atoms.index("moov") < atoms.index("mdat"), "MP4 not faststart"
    run("ffmpeg", "-v", "error", "-i", str(SOURCE), "-f", "null", "-")
    run("ffmpeg", "-v", "error", "-i", str(args.fixture), "-f", "null", "-")
    comparisons = []
    for seconds in (0, 1, 2, 3):
        original = frame(SOURCE, seconds)
        derived = frame(args.fixture, seconds).resize(original.size, Image.Resampling.LANCZOS)
        # Compare teacher lane and board separately; major crop/scale drift fails.
        errors = {}
        for name, box in (("teacher", (0, 0, 404, 720)), ("board", (404, 0, 1280, 720))):
            diff = ImageChops.difference(original.crop(box), derived.crop(box))
            errors[name] = round(sum(ImageStat.Stat(diff).mean) / 3, 4)
            assert errors[name] < 5, f"{name} composition drift at {seconds}s: {errors[name]}"
        comparisons.append({"seconds": seconds, "mean_absolute_pixel_error": errors})
        if seconds == 1:
            derived.save(evidence / "fixture-frame.png")
    # A dark-pixel bound is a geometric diagnostic, not semantic face recognition.
    # The approved panel is grey, so dark clothing/hair/shoes separate cleanly.
    bounds = []
    for seconds in (0, 5, 12, 20, 30, 40, 50, 60, 70, 75):
        im = frame(SOURCE, seconds)
        dark = Image.new("1", im.size)
        pixels = dark.load()
        for y in range(56, 664):
            for x in range(60, 350):
                if max(im.getpixel((x, y))) < 100:
                    pixels[x, y] = 1
        box = dark.getbbox()
        assert box and 60 < box[0] < box[2] < 350 and 56 < box[1] < box[3] < 664
        bounds.append({"seconds": seconds, "dark_person_bounds": box})
    report = {"source_sha256": SOURCE_HASH, "fixture_sha256": digest(args.fixture),
              "fixture_bytes": args.fixture.stat().st_size,
              "fixture_duration": info["format"]["duration"],
              "frame_size": [video["width"], video["height"]],
              "source_detail": "720p, uniformly upscaled for non-production transport test",
              "decode": "source and fixture passed", "faststart": True,
              "exact_math_examples": 5, "composition_comparisons": comparisons,
              "reference_geometry_samples": bounds,
              "not_verified": ["new voice generation", "native 1080p teacher detail",
                               "independent avatar compositing", "new narration alignment"]}
    (evidence / "media-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
