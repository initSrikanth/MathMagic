#!/usr/bin/env python3
"""MathMagic Mixed Numbers: animated classroom-board source generator.

Seven distinct visual steps follow the approved teacher narration.  Fractions
are rendered with a horizontal bar, never a slash.  Use the completed HeyGen
video's exact duration via --duration; inspect sync before publishing.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import subprocess
import cairosvg

W, H = 1920, 1080
INK = "#17334d"
BLUE = "#1674c7"
GREEN = "#21835a"
WHITE = "#ffffff"
# Speech sections: intro, 7/4, 11/4, 3 2/5, comparison, 9/4, recap.
WEIGHTS = [16, 26, 29, 34, 22, 21, 16]


def text(x, y, value, size=48, colour=INK, bold=False):
    import html
    return (f'<text x="{x}" y="{y}" fill="{colour}" font-size="{size}" '
            f'font-weight="{"bold" if bold else "normal"}" '
            f'font-family="DejaVu Sans,Arial,sans-serif">{html.escape(str(value))}</text>')


def frac(x, y, n, d, size=68):
    assert d > 0 and n >= 0
    return (text(x+22, y, n, size, bold=True)
            + f'<path d="M{x},{y+17} h{size+12}" stroke="{INK}" stroke-width="6"/>'
            + text(x+22, y+93, d, size, bold=True))


def mixed(x, y, whole, n, d):
    return text(x, y+47, whole, 80, bold=True) + frac(x+90, y, n, d, 65)


def parts(x, y, count, d=4, size=105):
    """Shaded quarter/fifth strips: each cell is one equal part of one whole."""
    assert d in (4, 5)
    out = []
    for i in range(count):
        cx = x + (i % d) * size
        cy = y + (i // d) * (size + 34)
        out.append(f'<rect x="{cx}" y="{cy}" width="{size}" height="{size}" '
                   f'fill="{GREEN if i < count else WHITE}" '
                   f'stroke="{INK}" stroke-width="4"/>')
    return "".join(out)


def bar(x, y, filled, d=4, width=440, height=72):
    assert 0 <= filled <= d
    cells = []
    for j in range(d):
        cx = x + j * width / d
        cells.append(f'<rect x="{cx}" y="{y}" width="{width/d}" height="{height}" '
                     f'fill="{GREEN if j < filled else WHITE}" stroke="{INK}" stroke-width="4"/>')
    return "".join(cells)


def board(title, subtitle, content):
    # Teacher lane x=0..320, classroom whiteboard x=340..1850.
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#e8e0d1"/>'
            '<rect y="875" width="1920" height="205" fill="#b78c68"/>'
            '<rect x="330" y="55" width="1550" height="805" rx="24" fill="#956d4a"/>'
            '<rect x="350" y="76" width="1510" height="762" rx="14" fill="#ffffff"/>'
            + text(420, 162, title, 62, INK, True)
            + text(420, 220, subtitle, 32, "#4b6880") + content + '</svg>')


def scenes():
    assert Fraction(7,4) == 1 + Fraction(3,4)
    assert Fraction(11,4) == 2 + Fraction(3,4)
    assert 3 + Fraction(2,5) == Fraction(17,5)
    assert 2 + Fraction(1,2) > 2 + Fraction(1,4)
    assert Fraction(9,4) == 2 + Fraction(1,4)
    result = []
    result.append(board("Mixed Numbers", "Fractions can represent more than one whole",
        text(550, 420, "Improper fraction", 55, BLUE, True)
        + frac(720, 515, 7, 4)
        + text(1120, 420, "Mixed number", 55, GREEN, True)
        + mixed(1200, 515, 1, 3, 4)))
    result.append(board("Seven quarters", "Four quarters make one whole; three quarters remain",
        frac(520, 330, 7, 4)
        + text(760, 422, "=", 80, BLUE, True)
        + mixed(910, 330, 1, 3, 4)
        + bar(570, 610, 4) + bar(1110, 610, 3)
        + text(680, 750, "1 whole", 40, GREEN, True)
        + text(1230, 750, "3 quarters", 40, GREEN, True)))
    result.append(board("Eleven quarters", "Eight quarters form two wholes, with three left",
        frac(550, 310, 11, 4)
        + text(805, 402, "=", 80, BLUE, True)
        + mixed(970, 310, 2, 3, 4)
        + bar(480, 590, 4, 360) + bar(890, 590, 4, 360)
        + bar(1300, 590, 3, 360)
        + text(560, 740, "1 whole", 35, GREEN, True)
        + text(975, 740, "1 whole", 35, GREEN, True)
        + text(1370, 740, "3 quarters", 35, GREEN, True)))
    result.append(board("Mixed to improper", "Multiply the whole number, then add the numerator",
        mixed(540, 330, 3, 2, 5)
        + text(880, 425, "=", 80, BLUE, True)
        + frac(1100, 330, 17, 5)
        + text(545, 610, "3 × 5 + 2 = 17", 58, GREEN, True)
        + text(545, 715, "Keep the denominator: 5", 44)))
    result.append(board("Compare mixed numbers", "Compare wholes first; if equal, compare fractional parts",
        mixed(530, 345, 2, 1, 2)
        + text(860, 445, ">", 110, BLUE, True)
        + mixed(1080, 345, 2, 1, 4)
        + bar(570, 640, 1, 2, 350) + bar(1090, 640, 1, 4, 350)
        + text(645, 770, "One half", 37, GREEN, True)
        + text(1175, 770, "One quarter", 37, GREEN, True)))
    result.append(board("Your turn: nine quarters", "Count two complete wholes and one quarter",
        frac(530, 330, 9, 4)
        + text(795, 422, "=", 80, BLUE, True)
        + mixed(990, 330, 2, 1, 4)
        + bar(480, 610, 4, 350) + bar(885, 610, 4, 350)
        + bar(1290, 610, 1, 350)))
    result.append(board("Remember", "A whole is made from equal-sized fractional parts",
        text(485, 355, "1. Divide numerator by denominator.", 46, INK, True)
        + text(485, 485, "2. The quotient gives complete wholes.", 46, INK, True)
        + text(485, 615, "3. The remainder gives fractional parts.", 46, INK, True)
        + text(485, 750, "Always keep the original denominator.", 42, GREEN, True)))
    assert len(result) == len(WEIGHTS) == len(set(result))
    return result


def run(duration, output):
    assert 10 < duration < 900
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = output.parent / "mixed_boards"
    frames_dir.mkdir(exist_ok=True)
    weights = [w * duration / sum(WEIGHTS) for w in WEIGHTS]
    playlist = []
    for i, (svg, seconds) in enumerate(zip(scenes(), weights), 1):
        frame = frames_dir / f"board_{i:02d}.png"
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(frame),
                         output_width=1280, output_height=720)
        playlist.extend([f"file '{frame.resolve()}'", f"duration {seconds:.6f}"])
    playlist.append(f"file '{frame.resolve()}'")
    filelist = frames_dir / "playlist.txt"
    filelist.write_text("\n".join(playlist) + "\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(filelist), "-vf", "fps=24,format=yuv420p",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-movflags", "+faststart", "-t", str(duration), str(output)], check=True)
    print(f"Rendered {len(WEIGHTS)} distinct scenes to {output} ({duration:.2f}s)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(args.duration, args.output)
