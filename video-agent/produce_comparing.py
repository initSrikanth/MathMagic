#!/usr/bin/env python3
"""Render Comparing Fractions with seven changing, mathematically checked boards.

Uses the EXISTING transparent presenter and narration. No paid HeyGen generation.
"""
import copy
import json
import subprocess
from pathlib import Path

import cairosvg
from agent import draw_scene, validate_scene
from production import download_video, render, qa_mp4

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "MathMagic_Comparing_Fractions_FINAL.mp4"
TMP = ROOT / "video-agent" / "output" / "comparing_final"
URL = "https://resource2.heygen.ai/aws_pacific/avatar_tmp/f45de351b0f64d64b92ccf9397642c65/75adeb4005e511a9aaa5af6372d7224e.webm"
DURATION = 110.942
# Scene boundaries are editable. Every scene MUST have a different visual.
SEGMENTS = [12, 19, 17, 16, 18, 15, DURATION - 97]


def custom_board(title, subtitle, contents):
    # The left 330 pixels are deliberately empty for the unframed presenter.
    return ('''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
    <rect width="1920" height="1080" fill="#e8e0d1"/>
    <rect y="875" width="1920" height="205" fill="#b78c68"/>
    <rect x="330" y="55" width="1550" height="805" rx="24" fill="#956d4a"/>
    <rect x="351" y="76" width="1508" height="763" rx="12" fill="#ffffff"/>
    <g fill="#142c45" font-family="DejaVu Sans,Arial,sans-serif">
    <text x="410" y="160" font-size="64" font-weight="bold">''' + title +
    '''</text><text x="410" y="220" font-size="28" fill="#567086">''' + subtitle +
    '''</text></g>''' + contents + '</svg>')


def label(x, y, s, size=40, colour="#142c45"):
    return f'<text x="{x}" y="{y}" fill="{colour}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" font-weight="bold">{s}</text>'


def fraction(x, y, n, d):
    return (label(x, y, str(n), 62) +
            f'<path d="M{x-9},{y+16} h74" stroke="#142c45" stroke-width="5"/>' +
            label(x, y+91, str(d), 62))


def intro_board():
    blocks = []
    for i, (symbol, name) in enumerate([("&lt;", "LESS THAN"), ("&gt;", "GREATER THAN"), ("=", "EQUAL TO")]):
        x = 465 + i * 455
        blocks.append(f'<rect x="{x}" y="300" width="375" height="320" rx="24" fill="#edf4ff" stroke="#a4c7ed" stroke-width="3"/>')
        blocks.append(label(x+126, 440, symbol, 105, "#1674c7"))
        blocks.append(label(x+45, 530, name, 31))
    return custom_board("Comparing Fractions", "Which fraction is greater, smaller or equal?", "".join(blocks))


def compare_scene(heading, a, b, relation):
    scene = {"heading": heading, "narration": "Compare fraction models.",
             "kind": "compare", "a": list(a), "b": list(b),
             "relation": relation, "seconds": 15}
    validate_scene(scene)
    return draw_scene(scene, "Comparing Fractions")


def numberline_board():
    parts = ['<path d="M520,530 H1700" stroke="#142c45" stroke-width="8"/>']
    for i, text in enumerate(["0", "1/4", "1/2", "3/4", "1"]):
        x = 520 + i*295
        parts.append(f'<path d="M{x},500 V560" stroke="#1674c7" stroke-width="6"/>')
        parts.append(label(x-25, 625, text, 43))
    parts.append(label(700, 760, "1/4  &lt;  1/2  &lt;  3/4", 58, "#1674c7"))
    return custom_board("Fractions on a number line", "Further to the right means greater", "".join(parts))


def challenge_board():
    parts = [fraction(750, 385, 2, 3), label(975, 450, "&gt;", 100, "#1674c7"),
             fraction(1190, 385, 1, 3),
             '<rect x="650" y="620" width="800" height="110" rx="22" fill="#e1f4e9"/>',
             label(825, 693, "2/3  &gt;  1/3", 65, "#167447")]
    return custom_board("Quick challenge", "Two thirds or one third: which is greater?", "".join(parts))


def summary_board():
    messages = ["1. Same denominator: compare numerators.",
                "2. Same numerator: smaller denominator gives larger parts.",
                "3. Otherwise: draw equal wholes or use equivalent fractions."]
    parts = []
    for i, message in enumerate(messages):
        y = 300 + 145*i
        parts.append(f'<rect x="450" y="{y}" width="1260" height="105" rx="16" fill="#edf4ff"/>')
        parts.append(label(485, y+68, message, 35))
    return custom_board("Remember these rules", "Three reliable ways to compare fractions", "".join(parts))


def run():
    TMP.mkdir(parents=True, exist_ok=True)
    boards = [
        intro_board(),
        compare_scene("Same denominator", (3, 5), (4, 5), "<"),
        compare_scene("Same numerator", (1, 2), (1, 4), ">"),
        compare_scene("Equivalent fractions", (1, 2), (2, 4), "="),
        numberline_board(),
        challenge_board(),
        summary_board(),
    ]
    assert len(boards) == len(SEGMENTS) == 7
    # Reject accidentally repeated or static teaching graphics before publishing.
    assert len(set(boards)) == len(boards), "Every teaching board must be distinct"
    assert all(seconds > 0 for seconds in SEGMENTS), "Scene timings must be positive"
    assert all(svg.startswith("<svg") and svg.endswith("</svg>") for svg in boards), "Invalid SVG board"
    assert abs(sum(SEGMENTS) - DURATION) < 0.001
    playlist_lines = []
    for i, (svg, seconds) in enumerate(zip(boards, SEGMENTS), 1):
        png = TMP / f"scene_{i:02d}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png),
                         output_width=1280, output_height=720)
        playlist_lines.extend([f"file '{png.resolve()}'", f"duration {seconds:.4f}"])
    playlist_lines.append(f"file '{png.resolve()}'")
    playlist = TMP / "playlist.txt"
    playlist.write_text("\n".join(playlist_lines) + "\n")
    board = TMP / "board.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(playlist), "-vf", "fps=24,format=yuv420p",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
                    "-movflags", "+faststart", str(board)], check=True)
    avatar = download_video(URL, TMP / "teacher.webm")
    OUT.parent.mkdir(exist_ok=True)
    render(board, avatar, OUT, max_seconds=DURATION)
    report = qa_mp4(OUT, min_seconds=100)
    if not report["passed"]:
        raise RuntimeError("Final MP4 QA failed: " + str(report))
    print(json.dumps({"qa": report, "scene_count": len(boards),
                      "scene_durations": SEGMENTS}, indent=2))


if __name__ == "__main__":
    run()
