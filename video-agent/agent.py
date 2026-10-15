#!/usr/bin/env python3
"""MathMagic video-agent: deterministic mathematics, board assets, QA and gated publishing.

No external API calls or paid operations occur in this module.
"""
import argparse
import html
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = Path(__file__).with_name("lessons.json")
OUTPUT = ROOT / "video-agent" / "output"


def value(pair):
    if not isinstance(pair, list) or len(pair) != 2:
        raise ValueError("Fraction must be [numerator, denominator]")
    n, d = pair
    if type(n) is not int or type(d) is not int or d <= 0 or n < 0:
        raise ValueError("Invalid nonnegative fraction")
    return Fraction(n, d)


def validate_scene(scene):
    kind = scene["kind"]
    if not (5 <= scene["seconds"] <= 120):
        raise ValueError("Scene length outside 5–120 seconds")
    if not scene.get("narration") or not scene.get("heading"):
        raise ValueError("Missing teaching text")
    if kind == "compare":
        a, b = value(scene["a"]), value(scene["b"])
        actual = "<" if a < b else ">" if a > b else "="
        if actual != scene["relation"]:
            raise ValueError(f"Incorrect comparison: {a} {scene['relation']} {b}")
    elif kind == "operation":
        a, b, result = value(scene["a"]), value(scene["b"]), value(scene["result"])
        if scene["op"] not in ("+", "-"):
            raise ValueError("Unsupported operator")
        actual = a + b if scene["op"] == "+" else a - b
        if actual != result:
            raise ValueError(f"Incorrect operation: expected {actual}, got {result}")
    elif kind == "mixed":
        improper = value(scene["improper"])
        mixed = scene["whole"] + value(scene["remainder"])
        if improper != mixed or scene["remainder"][0] >= scene["remainder"][1]:
            raise ValueError("Incorrect mixed number")
    elif kind == "numberline":
        if not 2 <= scene["denominator"] <= 12:
            raise ValueError("Invalid number-line denominator")
    else:
        raise ValueError(f"Unknown visual type: {kind}")


def validate(spec):
    if spec["schema_version"] != 1:
        raise ValueError("Unknown schema")
    ids, screens = set(), set()
    for lesson in spec["lessons"]:
        if lesson["id"] in ids or lesson["screen"] in screens:
            raise ValueError("Duplicate lesson id or screen")
        ids.add(lesson["id"])
        screens.add(lesson["screen"])
        if not lesson["scenes"]:
            raise ValueError("Empty lesson")
        for scene in lesson["scenes"]:
            validate_scene(scene)
    if len(spec["lessons"]) != 5:
        raise ValueError("Expected five fractions lessons")
    return sum(len(x["scenes"]) for x in spec["lessons"])


def txt(x, y, value, size=45, fill="#142c45", weight="bold"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-family="DejaVu Sans,Arial,sans-serif" font-weight="{weight}" fill="{fill}">{html.escape(str(value))}</text>'


def fraction(x, y, n, d):
    return (txt(x, y, n, 60) +
            f'<line x1="{x-8}" y1="{y+15}" x2="{x+62}" y2="{y+15}" stroke="#142c45" stroke-width="5"/>' +
            txt(x, y+83, d, 60))


def bar(x, y, pair, width=820, height=90):
    n, d = pair
    cells = []
    for i in range(d):
        px = x + width*i/d
        cells.append(f'<rect x="{px:.2f}" y="{y}" width="{width/d:.2f}" height="{height}" fill="{"#5aa2eb" if i<n else "#e4e9f0"}" stroke="#455a72" stroke-width="3"/>')
    return "".join(cells)


def draw_scene(scene, lesson_title):
    pieces = ['<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">',
        '<rect width="1920" height="1080" fill="#e8e0d1"/>',
        '<rect y="875" width="1920" height="205" fill="#b78c68"/>',
        '<rect x="330" y="55" width="1550" height="805" rx="24" fill="#956d4a"/>',
        '<rect x="351" y="76" width="1508" height="763" rx="12" fill="#ffffff"/>',
        txt(410,160,scene["heading"],64), txt(410,220,lesson_title,27,"#567086","normal")]
    # Keep the left 330 px clear for a full-body standing teacher.
    if scene["kind"] == "compare":
        pieces += [bar(520,300,scene["a"]), bar(520,460,scene["b"]),
                   fraction(825,660,*scene["a"]),txt(965,720,scene["relation"],76,"#1674c7"),
                   fraction(1110,660,*scene["b"])]
    elif scene["kind"] == "operation":
        pieces += [bar(520,315,scene["a"]),bar(520,475,scene["b"]),
                   fraction(610,680,*scene["a"]),txt(755,740,scene["op"],72),
                   fraction(880,680,*scene["b"]),txt(1030,740,"=",72),
                   fraction(1170,680,*scene["result"])]
    elif scene["kind"] == "mixed":
        n,d = scene["improper"]
        pieces += [fraction(640,470,n,d),txt(840,540,"=",70),
                   txt(1030,540,scene["whole"],76),
                   fraction(1160,470,*scene["remainder"])]
    else:
        d = scene["denominator"]
        pieces.append('<line x1="520" y1="530" x2="1660" y2="530" stroke="#142c45" stroke-width="8"/>')
        for i in range(d+1):
            x=520+1140*i/d
            pieces += [f'<line x1="{x}" y1="500" x2="{x}" y2="560" stroke="#1674c7" stroke-width="5"/>',
                       txt(x-22,625, f"{i}/{d}" if 0<i<d else str(i//d),32)]
    pieces.append('</svg>')
    return "\n".join(pieces)


def build(spec, output=OUTPUT):
    output.mkdir(parents=True,exist_ok=True)
    report = {"mode":"free_preparation","lessons":[]}
    for lesson in spec["lessons"]:
        folder = output/lesson["id"]
        folder.mkdir(parents=True,exist_ok=True)
        for index, scene in enumerate(lesson["scenes"],1):
            (folder/f"scene_{index:02d}.svg").write_text(draw_scene(scene,lesson["title"]),encoding="utf-8")
        (folder/"narration.txt").write_text("\n\n".join(s["narration"] for s in lesson["scenes"]),encoding="utf-8")
        report["lessons"].append({"id":lesson["id"],"scenes":len(lesson["scenes"]),
            "planned_seconds":sum(s["seconds"] for s in lesson["scenes"])})
    (output/"qa-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report


def render_preview(spec, output=OUTPUT):
    import cairosvg
    for lesson in spec["lessons"]:
        folder = output/lesson["id"]
        concat = []
        for index, scene in enumerate(lesson["scenes"],1):
            svg = folder/f"scene_{index:02d}.svg"
            png = folder/f"scene_{index:02d}.png"
            cairosvg.svg2png(url=str(svg),write_to=str(png),output_width=1280,output_height=720)
            concat += [f"file '{png.resolve()}'",f"duration {scene['seconds']}"]
        concat.append(f"file '{(folder/f'scene_{len(lesson['scenes']):02d}.png').resolve()}'")
        playlist = folder/"playlist.txt"
        playlist.write_text("\n".join(concat)+"\n")
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(playlist),
            "-vf","fps=24,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","25",
            "-movflags","+faststart",str(folder/"BOARD_ONLY_PREVIEW.mp4")],check=True)


def publish(spec, manifest_path, page_path):
    """Stage self-hosted embeds only for approved, independently hosted video URLs."""
    if not spec["settings"]["avatar_approved"]:
        raise ValueError("Avatar approval required before publication")
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    page = Path(page_path).read_text(encoding="utf-8")
    for lesson in spec["lessons"]:
        entry = manifest.get(lesson["id"],{})
        url = entry.get("url","")
        if entry.get("qa_passed") is not True or not url.startswith("https://") or not url.lower().split("?")[0].endswith(".mp4"):
            raise ValueError(f"Missing approved HTTPS MP4 for {lesson['id']}")
        start = page.index(f'<section id="{lesson["screen"]}"')
        end = page.index("</section>",start)+len("</section>")
        section = page[start:end]
        pattern = r'<div class="video-frame"><iframe\b[^>]*></iframe></div>'
        replacement = ('<div class="video-frame"><video controls playsinline preload="metadata" '
                       f'style="width:100%;height:100%" src="{html.escape(url,quote=True)}" '
                       f'aria-label="{html.escape(lesson["title"],quote=True)}"></video></div>')
        section, count = re.subn(pattern,lambda _:replacement,section,count=1)
        if count != 1:
            raise ValueError(f"Expected one existing video for {lesson['screen']}")
        page = page[:start]+section+page[end:]
    Path(page_path).write_text(page,encoding="utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=["validate","prepare","preview","publish"])
    parser.add_argument("--manifest")
    parser.add_argument("--page",default=str(ROOT/"fractions.html"))
    args=parser.parse_args()
    spec=json.loads(SPECS.read_text(encoding="utf-8"))
    count=validate(spec)
    print(f"PASS: {len(spec['lessons'])} lessons, {count} mathematically validated scenes")
    if args.command in ("prepare","preview"):
        report=build(spec)
        print(json.dumps(report,indent=2))
    if args.command=="preview":
        render_preview(spec)
    if args.command=="publish":
        if not args.manifest:
            parser.error("--manifest is required")
        publish(spec,args.manifest,args.page)


if __name__=="__main__":
    main()
