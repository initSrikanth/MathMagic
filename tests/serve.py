"""Local Playwright server with byte ranges, as used by static MP4 hosting."""

import re
import shutil
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class MediaHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.byte_range = None
        requested = self.headers.get("Range")
        if not requested:
            return super().send_head()
        path = self.translate_path(self.path)
        try:
            stream = open(path, "rb")
        except (OSError, ValueError):
            return super().send_head()
        stream.seek(0, 2)
        size = stream.tell()
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
        if match and any(match.groups()):
            first, last = match.groups()
            start = int(first) if first else max(0, size - int(last))
            end = min(int(last), size - 1) if first and last else size - 1
        else:
            start, end = size, -1
        if not 0 <= start <= end < size:
            stream.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        self.byte_range = (start, end)
        stream.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        return stream

    def copyfile(self, source, outputfile):
        if self.byte_range is None:
            return shutil.copyfileobj(source, outputfile)
        remaining = self.byte_range[1] - self.byte_range[0] + 1
        while remaining:
            block = source.read(min(64 * 1024, remaining))
            if not block:
                break
            outputfile.write(block)
            remaining -= len(block)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 4173), MediaHandler).serve_forever()
