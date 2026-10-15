#!/usr/bin/env python3
"""Produce Equivalent Fractions from the completed HeyGen WebM, without paid generation."""
import json
import subprocess
from pathlib import Path
import cairosvg
from agent import draw_scene
from production import download_video, render, qa_mp4

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"videos"/"MathMagic_Equivalent_Fractions_FINAL.mp4"
TMP=ROOT/"video-agent"/"output"/"equivalent_final"
URL="https://resource2.heygen.ai/aws_pacific/avatar_tmp/f45de351b0f64d64b92ccf9397642c65/48ed3cc55e0872196960d8ed67bbf5d7.webm"
DURATION=64.8882

def run():
    TMP.mkdir(parents=True,exist_ok=True)
    spec=json.loads((ROOT/"video-agent"/"lessons.json").read_text())
    lesson=next(x for x in spec["lessons"] if x["id"]=="equivalent")
    segments=[22,22,DURATION-44]
    concat=[]
    for i,(scene,seconds) in enumerate(zip(lesson["scenes"],segments),1):
        png=TMP/f"scene_{i:02d}.png"
        cairosvg.svg2png(bytestring=draw_scene(scene,lesson["title"]).encode(),write_to=str(png),output_width=1280,output_height=720)
        concat.extend([f"file '{png.resolve()}'",f"duration {seconds:.4f}"])
    concat.append(f"file '{png.resolve()}'")
    playlist=TMP/"playlist.txt"
    playlist.write_text("\n".join(concat)+"\n")
    board=TMP/"board.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(playlist),"-vf","fps=24,format=yuv420p","-c:v","libx264","-preset","ultrafast","-crf","24","-movflags","+faststart",str(board)],check=True)
    avatar=download_video(URL,TMP/"teacher.webm")
    OUT.parent.mkdir(exist_ok=True)
    render(board,avatar,OUT,max_seconds=DURATION)
    report=qa_mp4(OUT,min_seconds=60)
    if not report["passed"]:
        raise RuntimeError("Final MP4 QA failed: "+str(report))
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    run()
