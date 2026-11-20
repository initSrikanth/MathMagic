"""Statistics-only Pillow adapters for the existing production-v2 native renderer."""
import sys,math
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'production-v2'))
from graphics import text as txt,font,INK,TEAL,GOLD,BLUE,BG
# Avoid a same-name import when loaded by the runner: runner imports this as statistics_drawing.
CACHE={}
def text(d,s,x,y,size=66,fill=INK,center=False,maxw=1740):txt(d,str(s),x,y,size,fill,center,maxw)
def box(d,bounds,fill='#E7F2EC',outline=TEAL):d.rounded_rectangle(bounds,radius=24,fill=fill,outline=outline,width=4)
def panel(d,title):text(d,title,960,235,70,center=True)
def table(d,labels,counts,title='Checked responses',heading='Choice'):
 panel(d,title);x=330;y=345;w=1260;rh=90
 for j,(a,b) in enumerate([(heading,'Frequency')]+list(zip(labels,counts))):
  yy=y+j*rh;d.rectangle((x,yy,x+w,yy+rh),fill=TEAL if j==0 else ('#E7F2EC' if j%2 else 'white'),outline='#A8C6C2',width=2)
  text(d,a,x+40,yy+12,62,fill='white' if j==0 else INK,maxw=650);text(d,b,x+1000,yy+12,66,fill='white' if j==0 else INK,center=True,maxw=300)
 return [(x,y+(j+1)*rh,x+w,y+(j+2)*rh) for j in range(len(labels))]
def columns(d,labels,counts,title,axis='Choice',reveal=99):
 panel(d,title);left=240;right=1760;bottom=825;top=350;maximum=max(5,*counts);step=1 if maximum<=6 else 2;maximum=math.ceil(maximum/step)*step
 text(d,'Pupils',left,300,60)
 for n in range(0,maximum+1,step):
  y=bottom-(bottom-top)*n/maximum;d.line((left,y,right,y),fill='#BDD4D0',width=2);text(d,n,left-65,y-28,55,center=True)
 span=(right-left)/len(labels);bounds=[]
 for i,(label,n) in enumerate(zip(labels,counts)):
  x=left+i*span+span*.22;w=span*.56;y=bottom-(bottom-top)*n/maximum
  if i<=reveal:d.rectangle((x,y,x+w,bottom),fill=TEAL);text(d,n,x+w/2,max(310,y-75),64,center=True)
  text(d,label,x+w/2,850,64,center=True,maxw=span-15);bounds.append((x-10,y-10,x+w+10,bottom+10))
 text(d,axis,960,945,64,center=True);return bounds

def line(d,a,b=None,minimum=0,title='School garden tanks',reveal=99):
 panel(d,title);left=250;right=1720;top=370;bottom=800;maximum=max(50,*a,*(b or []));x=lambda i:left+i*(right-left)/(len(a)-1);y=lambda v:bottom-(v-minimum)*(bottom-top)/(maximum-minimum)
 text(d,'Litres',left,305,64)
 for n in range(minimum,maximum+1,10):
  yy=y(n);d.line((left,yy,right,yy),fill='#BDD4D0',width=2);text(d,n,left-75,yy-32,60,center=True)
 labels=['Mon','Tue','Wed','Thu'][:len(a)];bounds=[]
 for j,vs in enumerate([a,b] if b else [a]):
  color=BLUE if j else TEAL
  for i,v in enumerate(vs):
   if i>reveal:continue
   xx,yy=x(i),y(v)
   if i:
    last=(x(i-1),y(vs[i-1]));
    if j:
     for k in range(0,20,2):d.line((last[0]+(xx-last[0])*k/20,last[1]+(yy-last[1])*k/20,last[0]+(xx-last[0])*(k+1)/20,last[1]+(yy-last[1])*(k+1)/20),fill=color,width=7)
    else:d.line((*last,xx,yy),fill=color,width=7)
   if j:d.rectangle((xx-12,yy-12,xx+12,yy+12),fill=color)
   else:d.ellipse((xx-13,yy-13,xx+13,yy+13),fill=color)
   if not j:bounds.append((xx-30,yy-30,xx+30,yy+30))
 for i,label in enumerate(labels):text(d,label,x(i),835,64,center=True)
 text(d,'Time (equal day intervals)',960,930,62,center=True)
 if b:text(d,'A: solid circles     B: dashed squares',960,1010,54,center=True)
 return bounds

def model_for(lesson,parent):
 if lesson==1:return {'kind':'cards','labels':['Music','High','2 visits']} if parent==6 else {'kind':'types' if parent<9 else 'cycle'}
 if lesson==2 and parent==4:return {'kind':'cards','labels':['Apple','Banana','apple','Pear','Apple','Banana']}
 if lesson==2:return {'kind':'columns' if parent in [7,10,11] else 'table','labels':['Apple','Banana','Pear'],'counts':[3,2,1],'title':'Six checked snack votes','axis':'Snack'}
 if lesson==3:
  if parent==3:return {'kind':'counters','labels':['0','1','2','3','4'],'counts':[1,1,3,1,1],'title':'One counter for each pupil','axis':'Books borrowed'}
  if parent in [6,7]:return {'kind':'compare'}
  return {'kind':'columns','labels':['0','1','2','3','4'],'counts':[1,1,3,1,1] if parent<9 else [1,5,5,1,0],'title':'Library books borrowed','axis':'Books borrowed'}
 if lesson==4:return {'kind':'scale'} if parent==9 else {'kind':'line','a':[10,20,20,40],'b':[20,20,30,30] if parent in [6,7,8,10,11] else None}
 return {'kind':'cycle'} if parent<6 or parent>9 else {'kind':'table' if parent==9 else 'columns','labels':['Art','Sport','Music'] if parent==9 else ['Animals','Space','Sport','Other'],'counts':[4,3,1] if parent==9 else [4,3,2,1],'title':'8 of 24 replies' if parent==9 else 'Ten fictional class votes','axis':'Theme'}

def picture(l,c,folder,progress,elapsed,previous):
 now=c['start']+elapsed;model=c['statistics_model'];kind=model['kind'];boards=[e['text'] for e in c['board_events'] if e['at']<=now];reveal=99
 if (l['id']=='statistics-lesson4' and c['parent_index']==3) or kind=='counters' or (l['id']=='statistics-lesson2' and c['parent_index']==7) or (l['id']=='statistics-lesson5' and c['parent_index']==6):
  revealed=[e['index'] for e in c.get('parent_focus_events',[]) if e['at']<=now];reveal=max(revealed,default=-1)
 key=(l['id'],c['parent_index'],tuple(boards),str(model),reveal)
 if key not in CACHE:
  im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
  text(d,l['title'],960,30,82,center=True);d.line((110,145,1810,145),fill=TEAL,width=5)
  if c['role']=='success_criteria':
   for i,s in enumerate(c['board']):box(d,(100,260+i*230,1820,450+i*230));text(d,str(i+1)+'. '+s,960,315+i*230,62,center=True,maxw=1640)
  elif c['role']=='learning_goal':
   text(d,'Today we are learning…',960,250,82,center=True);box(d,(100,425,1820,705));text(d,l['learning_goal'],960,510,70,center=True,maxw=1640)
  else:
   if boards:text(d,boards[-1],960,165,62,fill=GOLD,center=True,maxw=1740)
   if kind=='table':table(d,model['labels'],model['counts'],model['title'])
   elif kind=='columns':columns(d,model['labels'],model['counts'],model['title'],model['axis'],reveal=reveal)
   elif kind=='line':line(d,model['a'],model.get('b'),reveal=reveal)
   elif kind=='cards':
    panel(d,'Responses to investigate')
    for i,label in enumerate(model['labels']):
     col=i%3;row=i//3;x=100+col*600;y=390+row*260;box(d,(x,y,x+520,y+190));text(d,label,x+260,y+55,74,center=True,maxw=480)
   elif kind=='counters':
    panel(d,model['title'])
    for i,(label,n) in enumerate(zip(model['labels'],model['counts'])):
     x=280+i*340;text(d,label,x,880,76,center=True)
     if i<=reveal:
      for j in range(n):d.ellipse((x-55,770-j*145,x+55,880-j*145),fill=TEAL)
    text(d,'Books borrowed',960,980,66,center=True)
   elif kind=='scale':
    # Same two observations; scales differ, never the data.
    text(d,'40 L → 50 L: read the scale',960,300,72,center=True)
    for j,mn in enumerate([0,40]):
     x=170+j*910;box(d,(x,425,x+790,890));text(d,'Scale starts at '+str(mn),x+395,465,62,center=True,maxw=730)
     for n in range(mn,51,10):
      yy=815-(n-mn)*240/(50-mn);text(d,n,x+100,yy-28,60,center=True);d.line((x+150,yy,x+710,yy),fill='#BDD4D0',width=2)
     d.line((x+230,815-(40-mn)*240/(50-mn),x+630,575),fill=TEAL,width=7);text(d,'Mon        Tue',x+450,840,54,center=True)
   elif kind=='compare':
    labels=['0','1','2','3','4'];as_=[1,2,5,2,1];bs=[0,0,5,4,2]
    table(d,labels,[f'{a}     |     {b}' for a,b in zip(as_,bs)],'Class A | Class B','Books')
   elif kind=='types':
    panel(d,'What does each response describe?')
    for i,(label,eg,meaning) in enumerate([('Nominal','Art • Sport • Music','Names'),('Ordinal','Low • Medium • High','Ordered groups'),('Discrete','0 • 1 • 2 visits','Counts')]):
     y=355+i*195;box(d,(120,y,1800,y+165));text(d,label,340,y+20,70,center=True,maxw=380);text(d,eg,1120,y+15,66,center=True,maxw=1100);text(d,meaning,1120,y+90,60,center=True)
   else:
    panel(d,'An investigation uses evidence')
    for i,label in enumerate(['Question','Plan','Collect','Check','Display','Report']):
     col=i%3;row=i//3;x=120+col*590;y=375+row*280;box(d,(x,y,x+540,y+205));text(d,str(i+1)+'. '+label,x+270,y+65,70,center=True,maxw=500)
  CACHE[key]=im
  if len(CACHE)>24:CACHE.pop(next(iter(CACHE)))
 im=CACHE[key].copy();d=ImageDraw.Draw(im)
 # Focus changes use recognised spoken label events, not a looping decoration.
 events=c.get('statistics_focus_events',[]);active=[e for e in events if e['at']<=now]
 if active and c['role'] not in ['learning_goal','success_criteria']:
  k=active[-1]['index']
  if kind=='types':d.rounded_rectangle((115,350+k*195,1805,525+k*195),radius=24,outline=GOLD,width=9)
  elif kind=='table':
   k=min(k,len(model['labels'])-1);d.rounded_rectangle((325,430+k*90,1595,525+k*90),radius=12,outline=GOLD,width=8)
  elif kind=='columns':
   k=min(k,len(model['labels'])-1);span=1520/len(model['labels']);d.rectangle((240+k*span,340,240+(k+1)*span,830),outline=GOLD,width=7)
  elif kind=='line':
   xx=250+min(k,3)*1470/3;d.line((xx,350,xx,810),fill=GOLD,width=6)
 return im
