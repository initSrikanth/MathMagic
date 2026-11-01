"""Bright fraction tiles; mathematical geometry only, no footage or figurative art."""
import sys,math
from pathlib import Path
from fractions import Fraction as Q
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'production-v2'))
# Import the existing, independently checked stacked-fraction primitives.
import importlib.util
spec=importlib.util.spec_from_file_location('owned_fraction_primitives',Path(__file__).resolve().parent.parent/'production-v2/graphics.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
W,H=1920,1080
BG='#FFF9EE';INK='#17354D';TEAL='#008A94';GOLD='#B85A10';PURPLE='#7550B5';EMPTY='#E1ECF3';EDGE='#6A8398'
def text(d,s,x,y,size=44,colour=INK,center=False,maxw=1680):g.text(d,str(s),x,y,size,colour,center,maxw)
def wrap(d,s,y,size=54,maxw=1640,colour=INK):
 lines=[];line=''
 for word in s.split():
  new=(line+' '+word).strip()
  if g.width(new,size)>maxw and line:lines.append(line);line=word
  else:line=new
 if line:lines.append(line)
 for line in lines:text(d,line,960,y,size,colour,True,maxw);y+=size*1.28
 return y

def equation(d,tokens,y=395,size=88):
 gap=34
 def width(t):return g.frac_width(t,size) if isinstance(t,list) else g.width(t,size)
 while sum(width(t) for t in tokens)+gap*(len(tokens)-1)>1640:size-=1
 assert size>=52,'Equation is too crowded'
 x=(W-sum(width(t) for t in tokens)-gap*(len(tokens)-1))/2
 for t in tokens:
  if isinstance(t,list):g.fraction(d,t,x,y,size,INK)
  else:text(d,t,x,y+18,size,TEAL if t in ['=','<','>','≠'] else INK)
  x+=width(t)+gap

def bars(d,rows,hide=False,partition=1,oldrows=None,first_y=610):
 compact=len(rows)>2 and first_y==610
 if compact:first_y=550
 gap,height,label_size,label_gap,value_size=(110,58,29,38,40) if compact else (160,70,33,48,46)
 wholes=max(max(1,math.ceil(r['n']/r['d'])) for r in rows);unit=1320/wholes
 for j,r in enumerate(rows):
  y=first_y+j*gap;n,den=r['n'],r['d'];chosen=Q(n,den);colour=TEAL if r['colour']=='teal' else GOLD
  text(d,r['label'],210,y-label_gap,label_size,maxw=1430)
  for k in range(wholes):
   left=210+k*unit;right=left+unit;d.rectangle((left,y,right,y+height),fill=EMPTY)
   amount=max(0,min(1,float(chosen-k)))
   if amount:d.rectangle((left,y,left+unit*amount,y+height),fill=colour)
  oldden=den
  if oldrows and j<len(oldrows) and Q(oldrows[j]['n'],oldrows[j]['d'])==chosen:oldden=oldrows[j]['d']
  for k in range(1,wholes*den):
   x=210+k*unit/den;is_old=(k*oldden)%den==0;length=height if is_old else round(height*partition)
   d.line((round(x),y,round(x),y+length),fill='white' if k<n else EDGE,width=3)
  for k in range(wholes+1):
   x=210+k*unit;d.line((round(x),y-1,round(x),y+height+1),fill=INK,width=5)
  if not hide:g.fraction(d,[n,den],1700,y-10,value_size,colour)

def line_model(d,l,progress):
 den=l['d'];total=den*l['maximum'];left=220;span=1450;y=730
 d.line((left,y,left+span,y),fill=INK,width=5)
 for i in range(total+1):
  x=left+span*i/total;d.line((x,y-13,x,y+13),fill=INK,width=3)
  if i%den==0:text(d,i//den,x,y+32,43,INK,True)
 for j,p in enumerate(l.get('points',[])):
  x=left+span*p/total;q=Q(p,den);col=TEAL if j%2==0 else GOLD
  d.ellipse((x-10,y-10,x+10,y+10),fill=col)
  value=[q.numerator,q.denominator]
  if q>=1 and q.denominator!=1:value=[q.numerator//q.denominator,q.numerator%q.denominator,q.denominator]
  if q.denominator==1:text(d,q.numerator,x,580,52,col,True)
  else:g.fraction(d,value,x-g.frac_width(value,48)/2,578,48,col)
  d.line((x,685,x,715),fill=col,width=3)
 if l.get('jump'):
  a,b=l['jump'];x1=left+span*a/total;x2=left+span*b/total;end=x1+(x2-x1)*progress
  d.line((x1,682,end,682),fill=GOLD,width=7)
  direction=1 if x2>x1 else -1
  if progress>.15:d.polygon([(end,682),(end-direction*16,672),(end-direction*16,692)],fill=GOLD)

def draw(lesson,cue,path,progress=1,oldcue=None,thinking=None):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 # Top 220px is a quiet overlay lane for native captions, away from controls/math.
 compact=len(cue.get('rows',[]))>2
 if not compact:text(d,lesson['title'],960,226,29,EDGE,True)
 role=cue.get('role');text(d,cue['chapter'],960,250 if compact else 280,48 if compact else 54,INK,True,maxw=1710)
 if role in ['goal','criteria','recap']:
  if role=='goal':
   wrap(d,cue['display'],380,66,colour=TEAL)
   if cue.get('rows'):bars(d,cue['rows'][:1],hide=True,first_y=715)
  elif role=='criteria':
   for i,s in enumerate(cue['criteria'][:cue['active']+1]):
    y=420+i*140;col=TEAL if i==cue['active'] else INK
    d.ellipse((165,y+10,191,y+36),fill=col);text(d,s,230,y,61,col,maxw=1500)
  else:
   wrap(d,cue['display'],375,50,colour=TEAL)
   for i,s in enumerate(cue['criteria']):text(d,s,960,550+i*110,51,INK,True,maxw=1600)
 else:
  if cue.get('equation') and not cue.get('hide_equation'):equation(d,cue['equation'],360 if compact else 395,72 if compact else 88)
  if cue.get('rows'):bars(d,cue['rows'],hide=cue.get('hide_labels',False),partition=progress,oldrows=oldcue.get('rows') if oldcue else None)
  if cue.get('area'):
   n,den=cue['area'];box=(725,565,1195,1035) if not cue.get('equation') else (775,555,1145,925)
   # Keep the diagram above native controls; a 330px model is sufficient.
   box=(810,550,1110,850)
   d.pieslice(box,-90,-90+360*n/den,fill=TEAL)
   d.ellipse(box,outline=INK,width=4)
   cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2;radius=(box[2]-box[0])/2
   for k in range(den):
    ang=math.radians(-90+360*k/den);d.line((cx,cy,cx+radius*math.cos(ang),cy+radius*math.sin(ang)),fill='white' if k<n else EDGE,width=4)
  if cue.get('line'):line_model(d,cue['line'],progress)
  if cue.get('board'):
   y=560
   for s in cue['board']:
    if '/' in s:
     import re
     parts=re.split(r'(\d+/\d+)',s);tokens=[list(map(int,p.split('/'))) if re.fullmatch(r'\d+/\d+',p) else p for p in parts if p.strip()]
     equation(d,tokens,y);y+=180
    else:wrap(d,s,y,48);y+=100
  if cue.get('note') and not cue.get('rows') and not cue.get('area') and not cue.get('board'):wrap(d,cue['note'],810,34)
 if thinking is not None:
  d.rounded_rectangle((570,90,1350,165),radius=20,fill='#E4F2F1')
  text(d,'Thinking time · '+str(thinking)+(' second' if thinking==1 else ' seconds'),960,108,39,TEAL,True)
 im.save(path)
