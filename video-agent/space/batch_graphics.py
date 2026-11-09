"""Space-specific measured diagrams; reuse the approved palette, type and renderer."""
import math,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent))
import importlib.util
_spec=importlib.util.spec_from_file_location('space_mesh_primitives',Path(__file__).with_name('graphics.py'));g=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(g)
INK,TEAL,GOLD,BG=g.INK,g.TEAL,g.GOLD,g.BG
SCENES={
 'net_cross':dict(kind='net',cells=[(1,0),(0,1),(1,1),(2,1),(1,2),(1,3)],valid=True),
 'net_t':dict(kind='net',cells=[(0,1),(1,1),(2,1),(3,1),(1,0),(1,2)],valid=True),
 'net_invalid':dict(kind='net',cells=[(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)],valid=False),
 'prism_net':dict(kind='prism_net',bad=False),'prism_bad':dict(kind='prism_net',bad=True),'pyramid_net':dict(kind='pyramid_net'),
 'cube':dict(kind='solid'),
 'origin':dict(kind='point',target=(0,0)),'point32':dict(kind='point',target=(3,2)),
 'point32_x':dict(kind='point',target=(3,0),label=(3,2)), 'point32_y':dict(kind='point',start=(3,0),target=(3,2)),
 'point64':dict(kind='point',target=(6,4)),'point25':dict(kind='point',target=(2,5)),
 'axis04':dict(kind='point',target=(0,4)),'axis40':dict(kind='point',target=(4,0)),
 'swapped':dict(kind='point',target=(2,5),other=(5,2)),
 'route7':dict(kind='route',path=[(1,1),(5,1),(5,4)]),
 'route7b':dict(kind='route',path=[(1,1),(1,4),(5,4)]),
 'route10':dict(kind='route',path=[(1,1),(5,1),(5,4),(7,4)]),
 'detour':dict(kind='route',path=[(1,1),(6,1),(5,1),(5,4)]),
 'missingroute':dict(kind='route',path=[(2,2),(6,2),(6,5)]),
 'scaledroute':dict(kind='route',path=[(1,1),(5,1),(5,4)],scale=10),
 'translate':dict(kind='translate',points=[(1,1),(3,1),(2,3)],vector=(3,2)),
 'translate_left':dict(kind='translate',points=[(4,2),(6,2),(5,4)],vector=(-2,1)),
 'translate_predict':dict(kind='translate',points=[(1,1),(3,1),(2,3)],vector=(2,3)),
 'reflect_v':dict(kind='reflect',points=[(1,1),(3,1),(2,3)],axis='x',line=4),
 'reflect_h':dict(kind='reflect',points=[(2,1),(4,1),(3,3)],axis='y',line=4),
 'reflect_on':dict(kind='reflect',points=[(4,2),(2,2),(3,4)],axis='x',line=4),
 'rotate_ccw':dict(kind='rotate',points=[(5,4),(7,4),(7,5),(6,5),(6,6),(5,6)],pivot=(4,4),angle=90),
 'rotate_cw':dict(kind='rotate',points=[(5,4),(7,4),(7,5),(6,5),(6,6),(5,6)],pivot=(4,4),angle=-90),
 'rotate_half':dict(kind='rotate',points=[(5,4),(7,4),(7,5),(6,5),(6,6),(5,6)],pivot=(4,4),angle=180),
 'sym_square':dict(kind='symmetry',shape='square',order=4),'sym_rectangle':dict(kind='symmetry',shape='rectangle',order=2),
 'sym_triangle':dict(kind='symmetry',shape='triangle',order=3),'sym_scalene':dict(kind='symmetry',shape='scalene',order=1),
 'class_square':dict(kind='classify',case='square'),'class_rectangle':dict(kind='classify',case='rectangle'),'class_rhombus':dict(kind='classify',case='rhombus'),'class_cube':dict(kind='classify',case='cube'),
 'design_translate':dict(kind='translate',points=[(1,2),(2,2),(1,3)],vector=(4,1)),
 'design_reflect':dict(kind='reflect',points=[(5,3),(6,3),(5,4)],axis='x',line=4),
 'exit_route':dict(kind='route',path=[(2,2),(5,2),(5,4)])}
DEFAULT={2:'net_cross',3:'prism_net',4:'point32',5:'route7',6:'translate',7:'reflect_v',8:'rotate_ccw',9:'class_square',10:'route7'}
BASE={}
def angle_events(c,m):
 """Native ASR word times for the explicitly narrated symmetry matches."""
 tokens=[(w['word'].lower(),w['start'])for w in c.get('words',[])if w['word'].lower()!='and'];events=[];cursor=0
 number_phrases={90:['ninety'],120:['one','hundred','twenty'],180:['one','hundred','eighty'],240:['two','hundred','forty'],270:['two','hundred','seventy'],360:['three','hundred','sixty']}
 targets=([90,180,270,360]if m['shape']=='square'else[180,360]if m['shape']=='rectangle'else[120,240,360]if m['shape']=='triangle'else[360])
 for target in targets:
  phrase=number_phrases[target];found=None
  for i in range(cursor,len(tokens)):
   if tokens[i][0]==str(target):found=(i,tokens[i][1]);break
   if [x[0]for x in tokens[i:i+len(phrase)]]==phrase:found=(i+len(phrase)-1,tokens[i+len(phrase)-1][1]);break
   if target in [180,360]and tokens[i][0]==('half'if target==180 else'full')and i+1<len(tokens)and tokens[i+1][0]=='turn':found=(i+1,tokens[i+1][1]);break
  if found:cursor=found[0]+1;events.append((min(c['speech_end'],found[1]+.12),target))
 return events
def spoken_angle(c,m,now,fallback):
 if '_angle_events'not in c:c['_angle_events']=angle_events(c,m)
 events=c['_angle_events']
 if not events:return fallback*360
 at,angle=c['motion_start'],0
 for target_at,target in events:
  if now<=target_at:
   move_at=min(target_at,max(at,at+.3 if angle else at));fraction=max(0,min(1,(now-move_at)/max(.05,target_at-move_at)));return angle+(target-angle)*fraction
  at,angle=target_at,target
 return angle
def txt(d,s,x,y,size=32,fill=INK):g.text(d,s,x,y,size,fill,True)
def project(p):return (510+p[0]*60,920-p[1]*60)
def dot(d,p,label='',fill=GOLD):
 x,y=project(p);d.ellipse((x-9,y-9,x+9,y+9),fill=fill,outline=INK,width=2)
 if label:txt(d,label,x+35,y-32,32)
def grid(d):
 for i in range(9):
  d.line((*project((i,0)),*project((i,8))),fill='#cadbd9',width=2);d.line((*project((0,i)),*project((8,i))),fill='#cadbd9',width=2)
  txt(d,str(i),510+i*60,947,30);txt(d,str(i),480,920-i*60,30)
 d.line((*project((0,8)),*project((0,0)),*project((8,0))),fill=INK,width=4)
 txt(d,'Horizontal',1115,950,32,TEAL);txt(d,'Vertical',465,410,32,TEAL)
def partial_path(d,path,p,color=GOLD):
 lengths=[abs(b[0]-a[0])+abs(b[1]-a[1])for a,b in zip(path,path[1:])];remaining=p*sum(lengths);current=path[0]
 for a,b,n in zip(path,path[1:],lengths):
  f=min(1,max(0,remaining/n)) if n else 1;current=(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f);d.line((*project(a),*project(current)),fill=color,width=8);remaining-=n
  if remaining<=0:break
 return current
def solid(d,p):
 points,faces,edges=g.mesh('cube');points=[(1080+(x-960)*.58,710+(y-650)*.58)for x,y in points]
 for face in faces[-3:]:d.polygon([points[i]for i in face],fill='#d9eeea',outline=TEAL,width=3)
 for i,(a,b)in enumerate(edges):d.line((*points[a],*points[b]),fill=GOLD if i<=int(p*len(edges)) else INK,width=4)
 txt(d,'Same faces, new directions',1100,922,29,TEAL)
def picture(l,c,folder,progress,elapsed,previous):
 now=c['start']+elapsed;board=tuple(e['text']for e in c['board_events']if e['at']<=now);cache=(l['id'],c['index'],board)
 if cache not in BASE:
  im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);txt(d,l['title'],960,115,43);txt(d,c['chapter'],960,197,37,TEAL)
  for i,line in enumerate(board):txt(d,line,960,265+49*i,32)
  BASE[cache]=im
  if len(BASE)>12:BASE.pop(next(iter(BASE)))
 im=BASE[cache].copy();d=ImageDraw.Draw(im);key=c['model']['key'];key=DEFAULT[int(l['id'].split('lesson')[1])]if key=='default' else key;m=SCENES[key];kind=m['kind'];question=c['role']=='question';p=0 if question else max(0,min(1,progress))
 # Every animation follows actual utterance/ASR clocks. Prediction results stay hidden.
 if kind=='net':
  cells=m['cells'];size=87;left=460;top=485
  for i,(x,y)in enumerate(cells):
   box=(left+x*size,top+y*size,left+(x+1)*size,top+(y+1)*size);d.rectangle(box,fill='#dcefe9',outline=INK,width=3)
   if not question and i<=int(p*5):d.rectangle(box,outline=GOLD,width=7)
   txt(d,str(i+1),left+(x+.5)*size,top+(y+.5)*size,30)
  if not question and m['valid']:solid(d,p)
  elif not m['valid']:
   txt(d,'Inspect the joins before folding',1130,640,31,TEAL)
   if not question:
    x,y=left+size,top+size;d.ellipse((x-18,y-18,x+18,y+18),outline=GOLD,width=7);txt(d,'Four squares meet at this flat corner',1130,720,29)
 elif kind=='solid':solid(d,p)
 elif kind=='prism_net':
  panels=[(0,0,4,2,'4 × 2'),(4,0,3,2,'3 × 2'),(7,0,4,2,'4 × 2'),(11,0,3,2,'3 × 2'),(0,-2 if m.get('bad') else -3,4,2 if m.get('bad') else 3,'4 × 2' if m.get('bad') else '4 × 3'),(0,2,4,3,'4 × 3')];s=52;ox,oy=490,640
  for i,(x,y,w,h,label)in enumerate(panels):
   box=(ox+x*s,oy+y*s,ox+(x+w)*s,oy+(y+h)*s);d.rectangle(box,fill='#dcefe9',outline=INK,width=3)
   if i<=int(p*5)and not question:d.rectangle(box,outline=GOLD,width=6)
   txt(d,label,ox+(x+w/2)*s,oy+(y+h/2)*s,27)
  txt(d,'Panel dimensions in centimetres',1120,465,31,TEAL)
 elif kind=='pyramid_net':
  x,y,s=840,620,140;polys=[[(x,y),(x+s,y),(x+s/2,y-140)],[(x+s,y),(x+s,y+s),(x+s+140,y+s/2)],[(x,y+s),(x+s,y+s),(x+s/2,y+s+140)],[(x,y),(x,y+s),(x-140,y+s/2)]]
  d.rectangle((x,y,x+s,y+s),fill='#dcefe9',outline=INK,width=4)
  for i,poly in enumerate(polys):d.polygon(poly,fill='#ffead0'if i<=int(p*4)and not question else '#e4eeeb',outline=INK,width=4)
  txt(d,'One square base',540,620,30,TEAL);txt(d,'Four matching triangular faces',1280,535,30,TEAL)
 elif kind in ['point','route','translate','reflect','rotate']:
  grid(d)
  if kind=='point':
   target=m['target'];label=m.get('label',target);dot(d,(0,0),'origin',TEAL);txt(d,'Target: ('+str(label[0])+', '+str(label[1])+')',1360,545,33,TEAL)
   if not question:
    at=partial_path(d,[m.get('start',(0,0)),(target[0],m.get('start',(0,0))[1]),target],p);dot(d,at)
    if p>.98:dot(d,target,'('+str(target[0])+', '+str(target[1])+')')
    if 'other'in m:dot(d,m['other'],'(5, 2)',TEAL)
  elif kind=='route':
   path=m['path'];dot(d,path[0],'Start',TEAL);dot(d,path[-1],'Destination',TEAL)
   if not question:dot(d,partial_path(d,path,p));
   txt(d,'Record each turn and position',1370,545,30,TEAL)
   if m.get('scale'):txt(d,'1 grid unit = 10 metres',1370,615,30)
  else:
   pts=m['points'];d.polygon([project(a)for a in pts],outline=TEAL,width=5)
   if kind=='translate':
    dx,dy=m['vector'];txt(d,('Right 'if dx>=0 else 'Left ')+str(abs(dx))+' • Up '+str(dy),1370,550,32,TEAL)
    if not question:
     new=[(x+dx*p,y+dy*p)for x,y in pts];d.polygon([project(a)for a in new],outline=GOLD,width=6);dot(d,new[0],"A′")
   elif kind=='reflect':
    axis,line=m['axis'],m['line'];a,b=((line,0),(line,8))if axis=='x'else((0,line),(8,line));d.line((*project(a),*project(b)),fill=GOLD,width=5);txt(d,'Mirror line '+axis+' = '+str(line),1370,545,32,TEAL)
    reflected=[(2*line-x,y)if axis=='x'else(x,2*line-y)for x,y in pts]
    if not question:
     count=min(3,1+int(p*3))
     for i,(a,b)in enumerate(zip(pts,reflected)):
      if i<count:d.line((*project(a),*project(b)),fill='#a5bcb9',width=3);dot(d,b,chr(65+i)+'′')
     if count==3:d.polygon([project(a)for a in reflected],outline=GOLD,width=5)
   else:
    cx,cy=m['pivot'];dot(d,(cx,cy),'Pivot',TEAL);txt(d,str(abs(m['angle']))+'° '+('anticlockwise'if m['angle']>0 else 'clockwise'),1370,545,30,TEAL)
    if not question:
     angle=math.radians(m['angle']*p);co,si=math.cos(angle),math.sin(angle);new=[(cx+(x-cx)*co-(y-cy)*si,cy+(x-cx)*si+(y-cy)*co)for x,y in pts];d.polygon([project(a)for a in new],outline=GOLD,width=5)
 elif kind=='symmetry':
  shape=m['shape'];pts=[(-125,-125),(125,-125),(125,125),(-125,125)]if shape=='square'else[(-195,-100),(195,-100),(195,100),(-195,100)]if shape=='rectangle'else[(190*math.cos(a),190*math.sin(a))for a in [-math.pi/2,math.pi/6,5*math.pi/6]]if shape=='triangle'else[(-130,290/3),(170,290/3),(-40,-580/3)]
  center=(940,690);d.polygon([(center[0]+x,center[1]+y)for x,y in pts],outline=TEAL,width=5)
  if not question:
   degrees=spoken_angle(c,m,now,p);a=math.radians(degrees);co,si=math.cos(a),math.sin(a);d.polygon([(center[0]+x*co-y*si,center[1]+x*si+y*co)for x,y in pts],outline=GOLD,width=5)
   txt(d,str(round(degrees))+'° turn',1380,620,36,TEAL)
  d.ellipse((934,684,946,696),fill=INK);txt(d,'Compare the turning shape with its original outline',960,985,29,TEAL)
 elif kind=='classify':
  case=m['case'];is3=case=='cube';nodes=[(960,470,'3D object?'if is3 else 'Four right angles?'),(610,625,'Six square faces?'if is3 else 'Four equal sides?'),(1310,625,'Examine flat shapes'if is3 else 'Four equal sides?'),(400,825,'Cube'if is3 else 'Square'),(800,825,'Other 3D object'if is3 else 'Non-square rectangle'),(1200,825,'Other group'if is3 else 'Non-square rhombus'),(1600,825,'Other group'if is3 else 'Other quadrilateral')]
  path=[0,1,3]if case in ['square','cube']else[0,1,4]if case=='rectangle'else[0,2,5];active=set(path[:min(3,1+int(p*3))])if not question else set()
  for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:d.line((nodes[a][0],nodes[a][1]+40,nodes[b][0],nodes[b][1]-40),fill=GOLD if a in active and b in active else '#adc7c2',width=4)
  for i,(x,y,label)in enumerate(nodes):
   d.rounded_rectangle((x-180,y-40,x+180,y+40),radius=12,fill='#e0f0ea',outline=GOLD if i in active else TEAL,width=4)
   txt(d,label if i<3 or not question else 'Predict the group',x,y,27)
  for x,y,label in [(740,540,'Yes'),(1190,540,'No'),(460,700,'Yes'),(750,700,'No'),(1210,700,'Yes'),(1510,700,'No')]:txt(d,label,x,y,28,TEAL)
  # Concrete property model remains visible beside the branching decisions.
  if case=='square':d.rectangle((200,515,330,645),fill='#dcefe9',outline=TEAL,width=5)
  elif case=='rectangle':d.rectangle((175,540,355,625),fill='#dcefe9',outline=TEAL,width=5)
  elif case=='rhombus':d.polygon([(265,500),(355,570),(265,640),(175,570)],fill='#dcefe9',outline=TEAL,width=5)
  else:
   ps,fs,es=g.mesh('cube');ps=[(265+(x-960)*.3,570+(y-650)*.3)for x,y in ps]
   for f in fs[-3:]:d.polygon([ps[i]for i in f],fill='#dcefe9',outline=TEAL,width=3)
  txt(d,'Test case: '+case,960,950,33,TEAL)
 if question and now>=c['speech_end']:txt(d,'Think and predict: '+str(max(0,math.ceil(c['end']-now))),960,1020,31,GOLD)
 return im
