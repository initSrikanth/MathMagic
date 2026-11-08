"""Programmatic models for the nine Space storyboards; coordinates are model units.
No decorative motion: traces, folds, slides, mirror construction and turns only.
"""
from PIL import Image,ImageDraw,ImageFont
import math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'video-agent/production-v2'))
from graphics import text as native_text,wrapped,INK,TEAL,GOLD,BG,font,width
# Rasterise each unchanged text label once. This preserves type and colours while
# avoiding font layout for every mathematical animation frame.
TEXT_CACHE={}
def text(d,s,x,y,size=40,fill=INK,center=False,maxw=1670):
 key=(str(s),size,fill,maxw)
 if key not in TEXT_CACHE:
  while width(s,size)>maxw:size-=1
  tw=width(s,size);tile=Image.new('RGBA',(math.ceil(tw)+3,size*2),(0,0,0,0))
  native_text(ImageDraw.Draw(tile),s,0,0,size,fill,False,maxw)
  TEXT_CACHE[key]=(tile,tw)
 tile,tw=TEXT_CACHE[key];d._image.paste(tile,(round(x-tw/2 if center else x),round(y)),tile)
COLORS=['#98dad0','#a8cee8','#ffd49a','#c5b9e6','#b9deb3','#f2b8b1']
CACHE={}

def smooth(p):return (1-math.cos(math.pi*max(0,min(1,p))))/2

def grid(d):
 left,base,step=610,925,65
 for k in range(11):
  x=left+k*step;y=base-k*step
  if k<=7:
   d.line((left,y,left+10*step,y),fill='#d0dddc',width=2);text(d,str(k),left-30,y-18,27,INK,True)
  d.line((x,base,x,base-7*step),fill='#d0dddc',width=2);text(d,str(k),x,base+10,27,INK,True)
 d.line((left,base,left+10*step+25,base),fill=INK,width=4)
 d.line((left,base,left,base-7*step-25),fill=INK,width=4)
 text(d,'Horizontal coordinate',900,970,29,TEAL,True)
 text(d,'Up',left-70,base-7*step-45,28,TEAL,True)
 return lambda pt:(left+step*pt[0],base-step*pt[1])

def dot(d,xy,label='',color=TEAL):
 x,y=xy;d.ellipse((x-9,y-9,x+9,y+9),fill=color,outline='white',width=2)
 if label:text(d,label,x+18,y-35,28,color)

def arrow(d,a,b,p=1,color=GOLD):
 x=a[0]+(b[0]-a[0])*p;y=a[1]+(b[1]-a[1])*p
 d.line((*a,x,y),fill=color,width=6)
 theta=math.atan2(b[1]-a[1],b[0]-a[0])
 if p>.01:
  d.polygon([(x,y),(x-17*math.cos(theta-.45),y-17*math.sin(theta-.45)),(x-17*math.cos(theta+.45),y-17*math.sin(theta+.45))],fill=color)

def polygon(d,pts,color=TEAL,fill=None):
 if fill:d.polygon(pts,fill=fill)
 d.line(pts+[pts[0]],fill=color,width=5,joint='curve')

def rotate_points(points,center,angle):
 a=math.radians(angle);co,si=math.cos(a),math.sin(a)
 return [[center[0]+co*(x-center[0])-si*(y-center[1]),center[1]+si*(x-center[0])+co*(y-center[1])]for x,y in points]

def folded_faces(cells,p):
 """Tree of edge hinges; full fold validated by six distinct face normals."""
 cells={tuple(c) for c in cells};root=(1,1) if (1,1) in cells else min(cells)
 frames={root:(np.zeros(3),np.array([1.,0,0]),np.array([0.,1,0]))};queue=[root]
 a=math.pi/2*p
 while queue:
  cell=queue.pop(0);c,u,v=frames[cell];n=np.cross(u,v)
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   nxt=(cell[0]+dx,cell[1]+dy)
   if nxt not in cells or nxt in frames:continue
   if dx:
    u2=u*math.cos(a)+n*dx*math.sin(a);v2=v;c2=c+dx*(u+u2)/2
   else:
    u2=u;v2=v*math.cos(a)+n*dy*math.sin(a);c2=c+dy*(v+v2)/2
   frames[nxt]=(c2,u2,v2);queue.append(nxt)
 return [np.array([c-u/2-v/2,c+u/2-v/2,c+u/2+v/2,c-u/2+v/2]) for c,u,v in frames.values()],frames

def net(d,m,p):
 kind=m['kind'];cells=m.get('cells',[])
 if kind=='net':
  if m.get('fold'):
   fs,_=folded_faces(cells,p)
   # fixed orthographic view; card geometry carries the movement.
   def project(pt):
    x,y,z=pt;return (960+180*(.88*x+.48*y),660+180*(.22*x-.4*y-.88*z))
   for i,f in sorted(enumerate(fs),key=lambda x:float(x[1].mean(axis=0) @ np.array([.4224,-.7744,.4576]))):
    d.polygon([project(v)for v in f],fill=COLORS[i%6],outline=INK,width=4)
   text(d,'Fold along shared edges',960,940,31,TEAL,True)
  else:
   lo=min(x for x,y in cells);hi=max(x for x,y in cells);top=min(y for x,y in cells);bottom=max(y for x,y in cells);s=min(125,500/(bottom-top+1));ox=960-(hi-lo+1)*s/2;oy=410
   for i,(x,y)in enumerate(cells):
    box=(ox+(x-lo)*s,oy+(y-top)*s,ox+(x-lo+1)*s,oy+(y-top+1)*s)
    d.rectangle(box,fill=COLORS[i%6],outline=INK,width=4)
   i=min(len(cells)-1,int(p*len(cells)));x,y=cells[i];d.rectangle((ox+(x-lo)*s+6,oy+(y-top)*s+6,ox+(x-lo+1)*s-6,oy+(y-top+1)*s-6),outline=GOLD,width=6)
   if m.get('invalid'):text(d,'Test this arrangement; do not assume it closes.',960,970,30,TEAL,True)
 elif kind=='boxnet':
  # Four 2x1 rectangles in a band, 1x1 squares on opposite sides.
  s=112;ox=848;oy=405
  for i in range(4):d.rectangle((ox,oy+i*s,ox+2*s,oy+(i+1)*s),fill=COLORS[i],outline=INK,width=4)
  for x in [-1,2]:d.rectangle((ox+x*s,oy+s,ox+(x+1)*s,oy+2*s),fill=COLORS[4 if x<0 else 5],outline=INK,width=4)
  text(d,'2 units',960,365,32,TEAL,True);text(d,'1',ox-56,oy+145,30,INK,True);text(d,'1',ox+280,oy+145,30,INK,True)
  text(d,'Four 2 by 1 rectangles; two 1 by 1 squares',960,935,30,TEAL,True)
  y=oy+min(4,p*4)*s;d.line((ox,y,ox+2*s,y),fill=GOLD,width=6)
 elif kind=='prismnet':
  # Equilateral triangular prism; rectangle widths exactly match triangle sides.
  side=140;length=250;ox=750;oy=570;h=side*math.sqrt(3)/2
  for i in range(3):d.rectangle((ox+i*side,oy,ox+(i+1)*side,oy+length),fill=COLORS[i],outline=INK,width=4)
  d.polygon([(ox+side,oy),(ox+2*side,oy),(ox+1.5*side,oy-h)],fill=COLORS[4],outline=INK,width=4)
  d.polygon([(ox+side,oy+length),(ox+2*side,oy+length),(ox+1.5*side,oy+length+h)],fill=COLORS[5],outline=INK,width=4)
  arrow(d,(ox,oy+length/2),(ox+3*side,oy+length/2),p)
  # A separate closed prism supports the flat-to-solid comparison.
  if m.get('fold'):
   a=[(1400,760),(1560,760),(1480,620)];b=[(x+90,y-70)for x,y in a]
   for poly in [a,b,[a[0],a[1],b[1],b[0]],[a[1],a[2],b[2],b[1]]]:d.polygon(poly,fill='#cce7df',outline=INK,width=3)
   for aa,bb in zip(a,b):d.line((*aa,*bb),fill=INK,width=3)
   text(d,'Closed prism',1520,840,27,TEAL,True)
 elif kind=='pyramidnet':
  s=220;ox=850;oy=600;h=s*math.sqrt(3)/2
  polys=[[(ox,oy),(ox+s,oy),(ox+s,oy+s),(ox,oy+s)],[(ox,oy),(ox+s,oy),(ox+s/2,oy-h)],[(ox+s,oy),(ox+s,oy+s),(ox+s+h,oy+s/2)],[(ox,oy+s),(ox+s,oy+s),(ox+s/2,oy+s+h)],[(ox,oy),(ox,oy+s),(ox-h,oy+s/2)]]
  for i,ps in enumerate(polys):d.polygon(ps,fill=COLORS[i],outline=INK,width=4)
  k=min(4,int(p*5));d.line(polys[k]+[polys[k][0]],fill=GOLD,width=7)

def grid_model(d,m,p,question=False):
 xy=grid(d);kind=m['kind'];hidden=m.get('hide',False) or question
 if kind=='grid':
  ps=m['points'];ls=m.get('labels',['']*len(ps))
  if m.get('hide'):return
  for i,pt in enumerate(ps):
   dot(d,xy(pt),ls[i] if i<len(ls) else '')
  if m.get('path') and len(ps)>1:
   for i in range(len(ps)-1):
    pp=max(0,min(1,p*(len(ps)-1)-i));arrow(d,xy(ps[i]),xy(ps[i+1]),pp)
  elif ps:
   x,y=ps[0];arrow(d,xy([0,0]),xy([x,0]),min(1,p*2));arrow(d,xy([x,0]),xy([x,y]),max(0,p*2-1))
 elif kind in ['translate','reflect']:
  pts=m.get('points',[[1,1],[3,1],[1,3]] if kind=='translate' else [[2,3],[4,3],[2,5]])
  if len(pts)>1:polygon(d,[xy(v)for v in pts],TEAL,'#d8efea')
  for i,pt in enumerate(pts):dot(d,xy(pt),'ABC'[i])
  if kind=='translate':target=[[x+m['dx'],y+m['dy']]for x,y in pts]
  else:
   axis=m['axis'];v=m['mirror'];target=[[2*v-x,y]if axis=='x' else [x,2*v-y]for x,y in pts]
   a,b=([v,0],[v,7])if axis=='x' else ([0,v],[10,v]);d.line((*xy(a),*xy(b)),fill='#8a469d',width=5)
   text(d,('x'if axis=='x' else'y')+' = '+str(v),1370,430,30,'#8a469d',True)
  if hidden:return
  for a,b in zip(pts,target):arrow(d,xy(a),xy(b),p)
  if kind=='translate':
   current=[[a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p]for a,b in zip(pts,target)]
   polygon(d,[xy(v)for v in current],GOLD)
  else:
   # Construction traces the perpendicular distance; image appears at end.
   if p>=.98:
    if len(target)>1:polygon(d,[xy(v)for v in target],GOLD)
  if p>=.98:
   for i,pt in enumerate(target):dot(d,xy(pt),'ABC'[i]+' image',GOLD)
 elif kind=='rotate':
  center=[4,4];src=[[6,4],[7,4],[6,5]];dot(d,xy(center),'Centre','#8a469d');polygon(d,[xy(v)for v in src],TEAL,'#d8efea')
  dot(d,xy(src[0]),'A')
  if hidden:return
  now=rotate_points(src,center,m['angle']*p);polygon(d,[xy(v)for v in now],GOLD)
  d.line((*xy(center),*xy(now[0])),fill=GOLD,width=4)
  trace=[xy(rotate_points([src[0]],center,m['angle']*p*j/40)[0])for j in range(41)];d.line(trace,fill=GOLD,width=5)
  if p>=.98:dot(d,xy(now[0]),'A image',GOLD)
 elif kind=='sequence':
  d.line((*xy([5,0]),*xy([5,7])),fill='#8a469d',width=5)
  text(d,'x = 5',1370,430,30,'#8a469d',True)
  ps=[[2,3]]if m['stage']==0 else [[2,3],[4,3],[6,3]]if m['stage']==2 else [[2,3],[8,3],[10,3]]
  for i,pt in enumerate(ps):dot(d,xy(pt),['Start','Step 1','Step 2'][i],TEAL if i==0 else GOLD)
  if len(ps)>1:
   for i in range(2):arrow(d,xy(ps[i]),xy(ps[i+1]),max(0,min(1,p*2-i)))

def symmetry(d,m,p,question):
 pts=[[-160,-160],[160,-160],[160,160],[-160,160]]if m['shape']=='square' else [[-240,-120],[240,-120],[240,120],[-240,120]]if m['shape']=='rectangle' else [[-190,-125],[220,-80],[65,180],[-100,100]]
 center=[960,670];original=[(x+center[0],center[1]-y)for x,y in pts];polygon(d,original,TEAL,'#d8efea');dot(d,center,'Centre','#8a469d')
 if question or m.get('hide'):return
 turn=360*p;current=rotate_points(pts,[0,0],turn);polygon(d,[(x+center[0],center[1]-y)for x,y in current],GOLD)
 text(d,f'Turn: {round(turn)} degrees anticlockwise',960,970,31,TEAL,True)
 # Exact match markers appear only after their angle is reached.
 angles=[90,180,270,360]if m['shape']=='square' else [180,360]if m['shape']=='rectangle' else [360]
 for i,a in enumerate(angles):
  if turn>=a-.1:text(d,str(a)+'°',710+i*160,395,30,GOLD,True)

def classify(d,m,p,question):
 if m['kind']=='classify':
  shapes=[[(460,700),(630,700),(630,870),(460,870)],[(820,730),(1060,730),(1060,850),(820,850)],[(1240,700),(1410,700),(1512,836),(1342,836)]]
  for ps in shapes:polygon(d,ps,TEAL,'#d8efea')
  for x,label in [(545,'Square'),(940,'Non-square rectangle'),(1365,'Non-square rhombus')]:text(d,label,x,900,28,INK,True)
  text(d,'Four equal sides?',960,415,37,TEAL,True)
  d.line((960,470,760,530),fill=INK,width=4);d.line((960,470,1210,530),fill=INK,width=4)
  text(d,'YES',770,475,27,TEAL,True);text(d,'NO',1190,475,27,TEAL,True)
  if not(question or m.get('hide')):
   text(d,'Four right angles?',740,545,33,INK,True);text(d,'Test other properties',1270,545,30,INK,True)
   arrow(d,(740,595),(545,665),min(1,p*2));arrow(d,(740,595),(1360,665),max(0,p*2-1))
   text(d,'YES',575,610,26,TEAL,True);text(d,'NO',1090,610,26,TEAL,True)
 else:
  def box(cx,w,h,depth):
   x=cx-w/2;y=760;dx=depth;dy=-depth*.55
   ps=[(x,y),(x+w,y),(x+w,y-h),(x,y-h)];polygon(d,ps,TEAL,'#d8efea')
   polygon(d,[(x,y-h),(x+dx,y-h+dy),(x+w+dx,y-h+dy),(x+w,y-h)],TEAL,'#b7ddd5')
   polygon(d,[(x+w,y),(x+w+dx,y+dy),(x+w+dx,y-h+dy),(x+w,y-h)],TEAL,'#a2cec5')
  box(635,180,180,90);box(1215,340,150,75)
  text(d,'Cube',680,835,35,INK,True);text(d,'Non-cube rectangular prism',1270,835,32,INK,True)
  if not(question or m.get('hide')):
   text(d,'Both have 6 faces. Compare face shapes and edges.',960,940,33,TEAL,True)
   d.line((520,780,520+min(1,p)*900,780),fill=GOLD,width=5)

def picture(l,c,folder,progress,elapsed,previous):
 now=c['start']+elapsed;board=tuple(e['text']for e in c['board_events']if e['at']<=now)
 key=(l['id'],c['index'],board)
 if key not in CACHE:
  im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
  text(d,l['title'],960,90,45,INK,True);text(d,c['chapter'],960,170,36,TEAL,True)
  for i,line in enumerate(board):text(d,line,960,240+48*i,31,INK,True)
  CACHE[key]=im
  if len(CACHE)>14:del CACHE[next(iter(CACHE))]
 im=CACHE[key].copy();d=ImageDraw.Draw(im);m=c['model'];question=c['role']=='question'
 p=smooth(max(0,min(1,(now-c['motion_start'])/max(.1,c['motion_end']-c['motion_start']))))
 if m['kind'] in ['net','boxnet','prismnet','pyramidnet']:net(d,m,p)
 elif m['kind'] in ['grid','translate','reflect','rotate','sequence']:grid_model(d,m,p,question)
 elif m['kind']=='symmetry':symmetry(d,m,p,question)
 else:classify(d,m,p,question)
 if question and now>=c['speech_end']:text(d,'Think and predict: '+str(max(0,math.ceil(c['end']-now))),960,1030,30,GOLD,True)
 return im
