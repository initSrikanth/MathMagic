"""Reuse approved Fractions typography/colour and extend its mathematical models."""
import importlib.util,math,re
from pathlib import Path
from decimal import Decimal
from PIL import Image,ImageDraw
spec=importlib.util.spec_from_file_location('approved_graphics',Path(__file__).resolve().parents[1]/'fractions-graphics-2026/graphics.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
g=f.g;W,H=1920,1080;BG=f.BG;INK=f.INK;TEAL=f.TEAL;GOLD=f.GOLD;EMPTY=f.EMPTY
text=f.text;wrap=f.wrap

def board(d,lines,y=380,size=55):
 for line in lines:
  if re.search(r'\d+/\d+',line):
   parts=re.split(r'(\d+/\d+)',line);tokens=[list(map(int,p.split('/'))) if re.fullmatch(r'\d+/\d+',p) else p for p in parts if p.strip()];f.equation(d,tokens,y,size);y+=145
  else:wrap(d,line,y,size);y+=size*1.5

def model(d,m,p):
 typ=m['type']
 if typ=='place':
  labels=m['labels'];cw=1500/len(labels);y=620
  for i,(label,digit) in enumerate(zip(labels,m['digits'])):
   x=210+i*cw;active=i==m.get('highlight',-1)
   d.rounded_rectangle((x,y,x+cw-8,y+185),radius=14,fill='#FFE4A5' if active else EMPTY)
   for k,line in enumerate(label.split('\n')):text(d,line,x+cw/2,y+14+k*34,30,INK,True,maxw=cw-16)
   text(d,digit,x+cw/2,y+103,68,TEAL,True)
   if active:d.line((x+15,y+180,x+15+(cw-40)*p,y+180),fill=GOLD,width=8)
 elif typ=='compare':
  labels=m['labels'];cw=1500/len(labels)
  for i,label in enumerate(labels):
   for k,line in enumerate(label.split('\n')):text(d,line,210+(i+.5)*cw,540+k*30,26,INK,True,maxw=cw-15)
  for j,digits in enumerate(m['numbers']):
   for i,digit in enumerate(digits):
    x=210+i*cw;y=620+j*105;active=i==m.get('highlight',-1)
    d.rounded_rectangle((x,y,x+cw-10,y+90),radius=12,fill='#FFE4A5' if active else EMPTY)
    text(d,digit,x+cw/2,y+15,57,TEAL if j==0 else GOLD,True)
 elif typ=='line':
  a=Decimal(str(m['start']));b=Decimal(str(m['end']));step=(b-a)/10;y=710
  d.line((220,y,1700,y),fill=INK,width=5)
  for i in range(11):
   x=220+148*i;d.line((x,y-15,x,y+15),fill=INK,width=3)
   if i%2==0:text(d,f'{a+i*step:.{m["decimals"]}f}',x,y+38,36,INK,True,maxw=150)
  if m.get('mark') is not None:
   x=220+1480*float((Decimal(str(m['mark']))-a)/(b-a));end=220+(x-220)*p
   d.line((220,650,end,650),fill=GOLD,width=7)
   d.polygon([(end,650),(end-16,640),(end-16,660)],fill=GOLD)
   d.ellipse((x-11,y-11,x+11,y+11),fill=TEAL);text(d,str(m['mark']),x,585,56,TEAL,True)
  text(d,'Equal step: '+f'{step:.{m["decimals"]}f}',960,800,38,INK,True)
 elif typ=='parts':
  den=m.get('den',10);n=m.get('n',1);x0=260;y=630;w=1400/den
  for i in range(den):d.rectangle((x0+i*w,y,x0+(i+1)*w,y+110),fill=TEAL if i<n*p else EMPTY,outline=INK,width=3)
  text(d,m.get('label','Equal-sized parts of one whole'),960,795,42,INK,True)
 elif typ=='tiles':
  values=m['values'];cw=1550/len(values)
  for i,v in enumerate(values):
   x=185+i*cw;d.rounded_rectangle((x,620,x+cw-15,770),radius=18,fill=TEAL if i%2==0 else GOLD)
   text(d,v,x+(cw-15)/2,660,52,'white',True,maxw=cw-35)
 elif typ=='array':
  r,c=m['rows'],m['cols'];cell=min(95,1250/c,230/r);left=(1920-c*cell)/2;top=550
  for row in range(r):
   for col in range(c):d.rounded_rectangle((left+col*cell,top+row*cell,left+(col+1)*cell-5,top+(row+1)*cell-5),radius=5,fill=TEAL if row*c+col<r*c*p else EMPTY)
  text(d,f'{r} equal '+('row' if r==1 else 'rows')+f' of {c}',960,805,42,INK,True)
 elif typ=='grid':
  n=m['n'];cell=25;x0=835;y0=535
  for i in range(100):
   x=x0+(i%10)*cell;y=y0+(i//10)*cell;d.rectangle((x,y,x+cell-2,y+cell-2),fill=TEAL if i<n*p else EMPTY)
  text(d,'100 equal parts in one whole',960,805,38,INK,True)
 elif typ=='bar':
  values=m['values'];total=sum(values);x=240;y=640
  for i,v in enumerate(values):
   w=1440*v/total;d.rectangle((x,y,x+w,y+110),fill=TEAL if i%2==0 else GOLD,outline='white',width=4)
   text(d,str(v),x+w/2,y+37,42,'white',True,maxw=w-12);x+=w
  text(d,m.get('label','Parts combine to make the whole'),960,810,40,INK,True)
 elif typ=='steps':
  for i,s in enumerate(m['steps'][:4]):
   x=130+i*430;d.rounded_rectangle((x,620,x+390,790),radius=18,fill=EMPTY);text(d,str(i+1),x+195,635,38,TEAL,True);text(d,s,x+195,705,36,INK,True,maxw=365)
 else:raise ValueError(typ)

def draw(lesson,cue,path,progress=1,oldcue=None,thinking=None):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);text(d,lesson['title'],960,226,29,f.EDGE,True);text(d,cue['chapter'],960,280,53,INK,True,maxw=1710)
 role=cue['role']
 if role=='goal':wrap(d,cue['display'],390,64,colour=TEAL)
 elif role=='criteria':
  for i,s in enumerate(cue['criteria'][:cue['active']+1]):
   y=420+i*140;d.ellipse((165,y+12,191,y+38),fill=TEAL);text(d,s,230,y,56,TEAL if i==cue['active'] else INK,maxw=1500)
 elif role=='recap':
  wrap(d,cue['display'],380,48,colour=TEAL)
  for i,s in enumerate(cue['criteria']):text(d,s,960,550+i*110,47,INK,True,maxw=1600)
 else:
  lines=cue.get('board',[]);assert len(lines)<=4
  board(d,lines,380,48 if len(lines)>2 else 57)
  if cue.get('model'):model(d,cue['model'],progress)
  elif not lines:model(d,lesson['default_model'],progress)
 if thinking is not None:
  d.rounded_rectangle((570,90,1350,165),radius=20,fill='#E4F2F1');text(d,'Thinking time · '+str(thinking)+' seconds',960,108,39,TEAL,True)
 im.save(path)
