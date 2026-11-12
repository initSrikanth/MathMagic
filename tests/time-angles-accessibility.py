"""Exact-source caption safety and scope audit; never re-synthesises/re-aligns media."""
import importlib.util
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('caption_guard',ROOT/'tools/video-quality/time_angles_accessibility.py')
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
r=guard.verify()
assert r['integrated_caption_sets']==5 and r['blocked_lessons']==[] and r['release_ready']is False
source=(ROOT/'js/time-angles.js').read_text();sequence=list(map(int,re.search(r'const sequence=\[([\d,\s]+)\]',source)[1].replace(' ','').split(',')))
assert len(sequence)==30 and not(set(sequence)&{2,3,4,8,9})
assert 'Timetables'not in source and 'signed integer'not in source
assert 'optional next-year'in(ROOT/'time-angles.html').read_text().lower()
assert 'i+=5'in(ROOT/'js/time-angles-graphics.js').read_text()
print(json.dumps(r,indent=2))
print('PASS: five hash-bound caption/transcript sets; Lesson 1 corrected candidate; original source preserved; full perceptual/release approval remains UNVERIFIED.')
