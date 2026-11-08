"""Restore archived, checksum-verified review bundles after a workspace replacement.
Never regenerate media or overwrite a different existing output.
"""
from pathlib import Path
import json,hashlib,shutil,sys
HERE=Path(__file__).parent;ARCHIVE=HERE/'review-media';OUT=Path('/workspace/output/space-review')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def restore(check_only=False):
 OUT.mkdir(parents=True,exist_ok=True);count=0
 for proof in sorted(ARCHIVE.glob('Space_Lesson*_qa.json')):
  qa=json.loads(proof.read_text());stem=proof.name[:-len('_qa.json')];video=ARCHIVE/(stem+'.mp4')
  assert sha(video)==qa['sha256'] and qa['full_decode'] and qa['full_audio_listened'] is False
  for source in ARCHIVE.glob(stem+'*'):
   if check_only:continue
   target=OUT/source.name
   if target.exists():assert sha(target)==sha(source),'Different existing file: '+str(target)
   else:shutil.copyfile(source,target)
  count+=1
 print(('CHECKED'if check_only else'RESTORED'),count,'archived review videos; perception still UNVERIFIED')
if __name__=='__main__':restore('--check' in sys.argv)
