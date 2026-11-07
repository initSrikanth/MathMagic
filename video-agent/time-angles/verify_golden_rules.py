"""Fail closed on Golden Video Rules before rendering or publishing."""
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ERRORS = []
for n in range(1, 6):
    path = ROOT / "video-agent" / "time-angles" / f"render_video{n}.py"
    if not path.exists():
        ERRORS.append(f"Lesson {n}: missing renderer")
        continue
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    beats = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BEATS" for t in node.targets):
            beats = ast.literal_eval(node.value)
            break
    if not beats:
        ERRORS.append(f"Lesson {n}: missing teaching beats")
        continue
    spoken = " ".join(str(b[1]) for b in beats)
    if re.search(r"math\s*magic|mathmagic", spoken, re.I):
        ERRORS.append(f"Lesson {n}: forbidden spoken brand")
    if any(re.search(r"math\s*magic|mathmagic", str(arg), re.I) for b in beats for arg in b[2:]):
        ERRORS.append(f"Lesson {n}: forbidden on-screen brand")
    roles = [b[0] for b in beats]
    if roles[0] != "hook" or roles[1] != "introduction":
        ERRORS.append(f"Lesson {n}: story must precede introduction")
    for required in ("goal", "criteria", "question", "answer", "misconception", "recap"):
        if required not in roles:
            ERRORS.append(f"Lesson {n}: missing {required}")
    if not any("Today we are learning" in b[1] for b in beats[:3]):
        ERRORS.append(f"Lesson {n}: missing lesson declaration")
    if "sid=31" not in source and "sid = 31" not in source:
        ERRORS.append(f"Lesson {n}: approved voice ID 31 not found")
    if "1920,1080" not in source and "1920, 1080" not in source:
        ERRORS.append(f"Lesson {n}: 1080p not configured")
    if len(beats) < 30:
        ERRORS.append(f"Lesson {n}: insufficient teaching progression ({len(beats)} beats)")
    print(f"Lesson {n}: {len(beats)} beats; narration branding check complete")
if ERRORS:
    print("\n".join(ERRORS), file=sys.stderr)
    sys.exit(1)
print("All five scripts pass pre-render Golden Rules checks.")
