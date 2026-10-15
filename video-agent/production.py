#!/usr/bin/env python3
"""MathMagic production transport and transparent-avatar compositor.

Network generation is always gated; read-only status/download are separate.
"""
import argparse
import io
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.heygen.com"


def require_paid_approval(approved, allow_paid):
    if not (approved and allow_paid and os.getenv("HEYGEN_API_KEY")):
        raise PermissionError("Paid generation requires approved avatar, --allow-paid and HEYGEN_API_KEY")


def heygen_request(path, method="GET", payload=None, api_key=None, opener=None):
    if not path.startswith("/") or path.startswith("//"):
        raise ValueError("API path must be relative")
    headers = {"X-Api-Key": api_key or os.getenv("HEYGEN_API_KEY", ""),
               "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API + path, data=body, headers=headers, method=method)
    with (opener or urllib.request.urlopen)(req, timeout=30) as response:
        result = json.load(response)
    if result.get("error"):
        raise RuntimeError("HeyGen API error")
    return result


def submit_transparent_video(script, pose_id, voice_id, *, approved=False, allow_paid=False, opener=None):
    require_paid_approval(approved, allow_paid)
    if not script.strip() or not pose_id or not voice_id:
        raise ValueError("Script, pose and voice are required")
    payload = {"avatar_pose_id": pose_id, "avatar_style": "normal",
               "input_text": script, "voice_id": voice_id,
               "dimension": {"width": 1920, "height": 1080}}
    result = heygen_request("/v1/video.webm", "POST", payload, opener=opener)
    video_id = result.get("data", {}).get("video_id")
    if not video_id:
        raise RuntimeError("HeyGen did not return video_id")
    return video_id


def get_video_status(video_id, opener=None):
    if not video_id or not all(c.isalnum() or c in "-_" for c in video_id):
        raise ValueError("Invalid video ID")
    result = heygen_request("/v1/video_status.get?video_id=" + video_id, opener=opener)
    return result.get("data") or result


def wait_for_video(video_id, *, timeout=1800, interval=20, opener=None, sleep=time.sleep):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = get_video_status(video_id, opener=opener)
        state = status.get("status")
        if state == "completed":
            url = status.get("video_url") or status.get("url")
            if not url:
                raise RuntimeError("Completed job has no downloadable URL")
            return url
        if state in ("failed", "cancelled"):
            raise RuntimeError("HeyGen job " + state)
        if state not in ("pending", "waiting", "processing", "queued"):
            raise RuntimeError("Unknown HeyGen status: " + str(state))
        sleep(interval)
    raise TimeoutError("HeyGen job timed out")


def download_video(url, target, opener=None):
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (host == "heygen.ai" or host.endswith(".heygen.ai")
            or host == "amazonaws.com" or host.endswith(".amazonaws.com")):
        raise ValueError("Untrusted HeyGen download URL")
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".part")
    try:
        with (opener or urllib.request.urlopen)(url, timeout=120) as response, temp.open("wb") as output:
            total = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > 1024 * 1024 * 1024:
                    raise ValueError("Download exceeds 1 GiB")
                output.write(block)
        if total < 1024:
            raise ValueError("Download unexpectedly small")
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)
    return target


def ffprobe(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                             "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def alpha_crop(webm, at=2):
    """Detect full-body alpha bounds using the VP9 decoder that preserves alpha."""
    from PIL import Image
    command = ["ffmpeg", "-loglevel", "error", "-c:v", "libvpx-vp9",
               "-ss", str(at), "-i", str(webm), "-frames:v", "1",
               "-vf", "format=rgba", "-f", "image2pipe", "-vcodec", "png", "-"]
    frame = subprocess.run(command, capture_output=True, check=True).stdout
    image = Image.open(io.BytesIO(frame)).convert("RGBA")
    mask = image.getchannel("A").point(lambda a: 255 if a >= 32 else 0)
    bounds = mask.getbbox()
    if not bounds:
        raise ValueError("No visible avatar in alpha frame")
    x0, y0, x1, y1 = bounds
    padding = 10
    x0, y0 = max(0, x0-padding), max(0, y0-padding)
    x1, y1 = min(image.width, x1+padding), min(image.height, y1+padding)
    return x0, y0, x1-x0, y1-y0


def render(board_video, avatar_webm, output, *, crop=None, max_seconds=None):
    board_video, avatar_webm, output = map(Path, (board_video, avatar_webm, output))
    for source in (board_video, avatar_webm):
        if not source.is_file():
            raise FileNotFoundError(source)
    info = ffprobe(avatar_webm)
    video = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    if video.get("codec_name") != "vp9" or video.get("tags", {}).get("ALPHA_MODE") != "1":
        raise ValueError("Expected transparent VP9 WebM; refusing destructive chroma key")
    x, y, w, h = crop or alpha_crop(avatar_webm)
    if min(w, h) <= 0:
        raise ValueError("Invalid avatar crop")
    factor = min(255/w, 600/h)
    ow, oh = max(2, int(w*factor)//2*2), max(2, int(h*factor)//2*2)
    top = 688-oh
    output.parent.mkdir(parents=True, exist_ok=True)
    filters = (f"[0:v]fps=24,scale=1280:720:flags=lanczos,format=rgba[board];"
               f"[1:v]crop={w}:{h}:{x}:{y},scale={ow}:{oh}:flags=lanczos,format=rgba[person];"
               f"[board][person]overlay=x=18:y={top}:format=auto,format=yuv420p[out]")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-threads", "2",
           "-i", str(board_video), "-c:v", "libvpx-vp9", "-threads", "2", "-i", str(avatar_webm),
           "-filter_complex", filters, "-map", "[out]", "-map", "1:a:0",
           "-c:v", "libx264", "-threads", "2", "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest"]
    if max_seconds:
        cmd.extend(["-t", str(max_seconds)])
    cmd.append(str(output))
    subprocess.run(cmd, check=True)
    return output


def qa_mp4(path, *, min_seconds=1):
    info = ffprobe(path)
    video = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    audio = next((s for s in info["streams"] if s.get("codec_type") == "audio"), {})
    duration = float(info["format"].get("duration", 0))
    result = {"path": str(path), "duration": round(duration, 2),
              "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name"),
              "width": video.get("width"), "height": video.get("height"),
              "pixel_format": video.get("pix_fmt")}
    result["passed"] = (video.get("codec_name") == "h264"
                        and audio.get("codec_name") == "aac"
                        and video.get("pix_fmt") == "yuv420p"
                        and video.get("width") == 1280
                        and video.get("height") == 720
                        and duration >= min_seconds)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["status", "fetch", "render", "qa", "generate"])
    for name in ("video-id", "url", "avatar-webm", "board", "output",
                 "script", "pose-id", "voice-id"):
        parser.add_argument("--" + name)
    parser.add_argument("--approved-avatar", action="store_true")
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--seconds", type=float)
    args = parser.parse_args()
    if args.command == "generate":
        if not args.script:
            parser.error("--script required")
        script = Path(args.script).read_text(encoding="utf-8")
        print(submit_transparent_video(script, args.pose_id, args.voice_id,
              approved=args.approved_avatar, allow_paid=args.allow_paid))
    elif args.command == "status":
        print(json.dumps(get_video_status(args.video_id), indent=2))
    elif args.command == "fetch":
        url = args.url or wait_for_video(args.video_id)
        print(download_video(url, args.output))
    elif args.command == "render":
        print(json.dumps(qa_mp4(render(args.board, args.avatar_webm,
                          args.output, max_seconds=args.seconds)), indent=2))
    elif args.command == "qa":
        print(json.dumps(qa_mp4(args.output), indent=2))


if __name__ == "__main__":
    main()
