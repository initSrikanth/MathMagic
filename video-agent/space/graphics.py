"""Exact polyhedral meshes, progressive feature highlighting and readable teaching boards."""
from PIL import Image,ImageDraw
from pathlib import Path
import sys,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'production-v2'))
import importlib.util
_sp=importlib.util.spec_from_file_location('space_primitives',Path(__file__).resolve().parents[1]/'production-v2/graphics.py');_g=importlib.util.module_from_spec(_sp);_sp.loader.exec_module(_g)
text,wrapped,INK,TEAL,GOLD,BG=_g.text,_g.wrapped,_g.INK,_g.TEAL,_g.GOLD,_g.BG
# In metres/units, not inferred from projected screen distances.
def mesh(kind):
 if kind=='prism':
  points=[(720,800),(1040,800),(880,530),(870,700),(1190,700),(1030,430)]
  faces=[[0,1,2],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]]
  edges=[(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5)]
 elif kind=='pyramid':
  points=[(700,790),(1020,790),(1190,675),(870,675),(945,450)]
  faces=[[0,1,2,3],[0,1,4],[1,2,4],[2,3,4],[3,0,4]];edges=[(0,1),(1,2),(2,3),(3,0),(0,4),(1,4),(2,4),(3,4)]
 else:
  points=[(740+x*260+y*140,800-y*100-z*250)for z in range(2)for y in range(2)for x in range(2)]
  faces=[[0,2,6,4],[1,3,7,5],[0,1,5,4],[2,3,7,6],[0,1,3,2],[4,5,7,6]]
  edges=[(4,5),(5,7),(7,6),(6,4),(0,1),(1,3),(3,2),(2,0),(0,4),(1,5),(2,6),(3,7)]
 assert len(points)-len(edges)+len(faces)==2
 assert all(sum(a in f and b in f for f in faces)==2 for a,b in edges)
 return points,faces,edges
BASE={}
def picture(l,c,folder,progress,elapsed,previous):
 now=c['start']+elapsed;board=tuple(e['text']for e in c['board_events']if e['at']<=now)
 key=(c['index'],board)
 if key not in BASE:
  im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);text(d,l['title'],960,135,42,INK,True);text(d,c['chapter'],960,215,38,TEAL,True)
  for i,line in enumerate(board):text(d,line,960,280+i*52,35,INK,True)
  BASE[key]=im
 im=BASE[key].copy();d=ImageDraw.Draw(im);m=c['model'];ps,faces,edges=mesh(m['kind']);stage=m['stage'];p=max(0,min(1,(now-c['motion_start'])/max(.1,c['speech_end']-c['motion_start'])))
 for face in faces[-3:]:d.polygon([ps[i]for i in face],fill='#e0f0eb',outline='#b5c9c8',width=2)
 for i,(a,b) in enumerate(edges):d.line((*ps[a],*ps[b]),fill=INK,width=4)
 n=len(faces)if stage=='faces' else len(edges)if stage=='edges' else len(ps)
 k=min(n-1,int(p*n))
 if c['role']=='question':pass
 elif stage=='faces':d.polygon([ps[i]for i in faces[k]],fill='#ffc982',outline=GOLD,width=5)
 elif stage=='edges':
  for a,b in edges[:k+1]:d.line((*ps[a],*ps[b]),fill=GOLD,width=8)
 else:
  for x,y in ps[:k+1]:d.ellipse((x-12,y-12,x+12,y+12),fill=GOLD,outline=INK,width=2)
 for i in range(0 if c['role']=='question' else n):
  x=960-(n-1)*48/2+i*48;d.ellipse((x-14,865,x+14,893),fill=GOLD if i<=k else '#d7e2df',outline=INK,width=2)
 text(d,'Transparent model: include hidden features',960,925,31,TEAL,True)
 if c['role']=='question' and now>=c['speech_end']:
  remain=max(0,5-(now-c['speech_end']));text(d,'Think and predict: '+str(math.ceil(remain)),960,990,30,GOLD,True)
 return im
