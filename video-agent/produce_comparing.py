#!/usr/bin/env python3
"""Produce Comparing Fractions from the completed HeyGen WebM, without paid generation."""
import json
import subprocess
from pathlib import Path
import cairosvg
from agent import draw_scene
from production import download_video, render, qa_mp4

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"videos"/"MathMagic_Comparing_Fractions_FINAL.mp4"
TMP=ROOT/"video-agent"/"output"/"comparing_final"
URL="https://resource2.heygen.ai/aws_pacific/avatar_tmp/f45de351b0f64d64b92ccf9397642c65/75adeb4005e511a9aaa5af6372d7224e.webm"
DURATION=110.942

def run():
    TMP.mkdir(parents=True,exist_ok=True)
    spec=json.loads((ROOT/"video-agent"/"lessons.json").read_text())
    lesson=next(x for x in spec["lessons"] if x["id"]=="comparing")
    segments=[18,25,24,21,DURATION-88]
    # Each board scene follows the Comparing Fractions curriculum, never Equivalent Fractions.\n    assert len(lesson["scenes"]) == len(segments), "Narration and scene count must agree"\n    concat=[]
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
