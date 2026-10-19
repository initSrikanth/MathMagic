"""1920×1080 geometry, with equal wholes and stacked fractions throughout."""
from PIL import Image, ImageDraw, ImageFont
import math
import re
W,H=1920,1080
BG='#FFF9EF'; INK='#183647'; TEAL='#087F7A'; GOLD='#A95704'; BLUE='#1768B2'; EMPTY='#DCECE6'; MUTED='#455D68'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(size): return ImageFont.truetype(FONT,size)
def width(s,size): return ImageDraw.Draw(Image.new('RGB',(1,1))).textlength(str(s),font=font(size))
def text(d,s,x,y,size=40,fill=INK,center=False,maxw=1670):
    while width(s,size)>maxw: size-=1
    d.text((x,y),str(s),font=font(size),fill=fill,anchor='mt' if center else 'lt')
def wrapped(d,s,y,size=38,maxw=1650,fill=MUTED):
    lines=[]; line=''
    for w in s.split():
        if width((line+' '+w).strip(),size)>maxw:
            lines.append(line); line=w
        else: line=(line+' '+w).strip()
    if line: lines.append(line)
    for l in lines:
        text(d,l,W/2,y,size,fill,True,maxw); y+=size*1.45
    return y

def frac_width(t,size):
    if len(t)==3: return width(t[0],size)+30+frac_width(t[1:],size)
    return max(width(t[0],size),width(t[1],size))+20

def fraction(d,t,x,y,size=64,fill=INK):
    if len(t)==3:
        text(d,t[0],x,y+size*.25,size,fill); x+=width(t[0],size)+30; t=t[1:]
    w=frac_width(t,size)
    text(d,t[0],x+w/2,y-size*.48,size,fill,True)
    d.line((x,y+size*.68,x+w,y+size*.68),fill=fill,width=4)
    text(d,t[1],x+w/2,y+size*.86,size,fill,True)

def equation(d,tokens,y=290):
    size=65; gap=32
    def tw(t): return frac_width(t,size) if isinstance(t,list) else width(t,size)
    while sum(tw(t) for t in tokens)+gap*(len(tokens)-1)>1620: size-=1
    x=(W-sum(tw(t) for t in tokens)-gap*(len(tokens)-1))/2
    for t in tokens:
        if isinstance(t,list): fraction(d,t,x,y,size)
        else: text(d,t,x,y+12,size,TEAL if t in ['=','>','<','≠'] else INK)
        x+=tw(t)+gap

def draw(lesson,cue,path,progress=1):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rounded_rectangle((45,35,1875,1035),radius=35,fill='white',outline='#DBE7DF',width=3)
    text(d,'MathMagic',90,65,32,TEAL)
    text(d,lesson['title'],1830-width(lesson['title'],30),68,30,MUTED,maxw=1400)
    d.line((90,130,1830,130),fill=EMPTY,width=3)
    text(d,cue['chapter'],W/2,175,51,INK,True)
    if cue.get('equation'): equation(d,cue['equation'])
    rows=cue.get('rows',[])
    if rows:
        # A whole has the same length in every row, even with mixed numbers.
        wholes=max(max(1,math.ceil(r['n']/r['d'])) for r in rows)
        unit=1260/wholes
        for j,r in enumerate(rows):
            y=490+j*170; n,den=r['n'],r['d']; cell=unit/den
            text(d,r['label'],260,y-48,30,MUTED)
            count=max(1,math.ceil(n/den))*den
            for i in range(count):
                x=260+i*cell
                fill=TEAL if r['colour']=='teal' else GOLD
                d.rectangle((round(x),y,round(x+cell),y+58),fill=fill if i<n*progress else EMPTY,outline='white',width=2)
            for k in range(count//den+1):
                x=260+k*unit; d.line((x,y,x,y+58),fill=INK,width=4)
            fraction(d,[n,den],1580,y-9,37,TEAL)
    l=cue.get('line')
    if l:
        y=610; x0=210; span=1500; den=l['d']; total=den*l['maximum']
        d.line((x0,y,x0+span,y),fill=MUTED,width=5)
        for i in range(total+1):
            x=x0+span*i/total
            d.line((x,y-16,x,y+16),fill=INK,width=3)
            if i%den==0: text(d,i//den,x,y+34,35,INK,True)
            elif total<=8: fraction(d,[i,den],x-23,y+40,29,MUTED)
        for j,p in enumerate(l['points']):
            x=x0+span*p/total
            if progress>.3:
                d.ellipse((x-11,y-11,x+11,y+11),fill=TEAL)
                fraction(d,[p,den],x-30,y-140,39,TEAL)
        jump=l.get('jump')
        if jump:
            a,b=jump; x1=x0+span*a/total; x2=x0+span*b/total
            xe=x1+(x2-x1)*progress
            d.line((x1,y-30,xe,y-30),fill=GOLD,width=7)
    if cue.get('area'):
        n,den=cue['area']; box=(735,445,1185,895)
        for i in range(den):
            d.pieslice(box,-90+i*360/den,-90+(i+1)*360/den,fill=TEAL if i<n*progress else EMPTY,outline='white',width=5)
    board=cue.get('board',[])
    # Concept diagrams for new topics also appear during openings and recaps.
    if not board and not cue.get('equation') and not rows and not l and not cue.get('area') and not cue.get('model'):
        topic=lesson['topic']; section=lesson['section']
        if topic=='addition-subtraction':
            wrapped(d,'Parts combine to make a total.',320,48)
            d.rounded_rectangle((300,520,1620,650),radius=12,fill=EMPTY,outline=INK,width=3)
            d.rectangle((300,520,970,650),fill=TEAL)
            text(d,'Known part',635,562,40,'white',True)
            text(d,'Other part',1295,562,40,INK,True)
            d.line((300,710,1620,710),fill=INK,width=4)
            text(d,'Total',960,750,44,INK,True)
            wrapped(d,'Add parts • Find a difference • Check the relationship',875,32)
        elif topic=='multiplication-division':
            division=section in ['lesson3','lesson4']
            if division:
                wrapped(d,'Equal groups: the whole is shared fairly.',320,44)
                for j in range(6):
                    x=230+j*250
                    d.rounded_rectangle((x,500,x+210,700),radius=20,fill=EMPTY,outline=TEAL,width=4)
                    text(d,'equal',x+105,565,32,INK,True)
                wrapped(d,'Number of groups × Amount in each group = Total',800,38)
            else:
                wrapped(d,'Four rows of eight: count equal groups.',320,44)
                for row in range(4):
                    for col in range(8):
                        x=580+col*105;y=500+row*82
                        d.ellipse((x,y,x+45,y+45),fill=TEAL if (row*8+col)<32*progress else EMPTY)
                text(d,'4 × 8 = 32',W/2,870,49,TEAL,True)
        elif topic=='factors-multiples':
            wrapped(d,'An array connects factors and their product.',320,44)
            for row in range(4):
                for col in range(6):
                    x=660+col*110;y=500+row*82
                    d.rectangle((x,y,x+62,y+52),fill=TEAL if row*6+col<24*progress else EMPTY)
            text(d,'4 × 6 = 24',W/2,865,49,TEAL,True)
        elif topic=='decimals-percentages':
            if section=='place':
                wrapped(d,'Place value continues to the right of the decimal point.',310,40)
                labels=['Ones','Tenths','Hundredths','Thousandths']
                for j,(label,digit) in enumerate(zip(labels,'4307')):
                    x=280+j*340
                    d.rounded_rectangle((x,500,x+320,740),radius=15,fill=EMPTY)
                    text(d,label,x+160,540,32,INK,True)
                    text(d,digit,x+160,635,62,TEAL,True)
                text(d,'4.307 = 4 ones + 3 tenths + 7 thousandths',W/2,850,39,TEAL,True)
            elif section=='compare':
                wrapped(d,'Compare positions, rather than counting written digits.',310,40)
                y=660; left=220; span=1480
                d.line((left,y,left+span,y),fill=INK,width=4)
                for j in range(11):
                    x=left+span*j/10
                    d.line((x,y-12,x,y+12),fill=INK,width=3)
                text(d,'0.5',left,y+40,35,INK,True)
                text(d,'0.7',left+span,y+40,35,INK,True)
                for j,v in enumerate([.599,.620]):
                    x=left+span*(v-.5)/.2
                    d.ellipse((x-9,y-9,x+9,y+9),fill=TEAL)
                    text(d,f'{v:.3f}',x,y-70-j*65,35,TEAL,True)
                text(d,'0.620 > 0.599',W/2,850,44,TEAL,True)
            else:
                wrapped(d,'One whole divided into one hundred equal parts.',305,42)
                for row in range(10):
                    for col in range(10):
                        x=730+col*46;y=425+row*46
                        d.rectangle((x,y,x+43,y+43),fill=TEAL if row*10+col<75*progress else EMPTY)
                text(d,'75 hundredths = 0.75 = 75%',W/2,920,37,TEAL,True)
    if board:
        size=min(52,200//max(1,len(board))+12)
        y=300 if not cue.get('equation') else 470
        for j,line in enumerate(board):
            # Handle source fraction notation as structured numerator/bar/denominator.
            if re.search(r'\d+/\d+',line):
                parts=re.split(r'(\d+/\d+)',line)
                tokens=[list(map(int,p.split('/'))) if re.fullmatch(r'\d+/\d+',p) else p for p in parts if p.strip()]
                equation(d,tokens,y)
                y+=155
            else:
                text(d,line,W/2,y,size,TEAL if j==len(board)-1 and progress>.5 else INK,True)
                y+=size*1.55
        # Progressive underline guides attention through the current worked step.
        d.line((300,y+12,300+1320*progress,y+12),fill=TEAL,width=5)
    model=cue.get('model')
    if model and model['type']=='place':
        labels=model['labels']; digits=model['digits']; cw=1500/len(labels); y=700
        for i,(label,digit) in enumerate(zip(labels,digits)):
            x=210+i*cw
            d.rounded_rectangle((x,y,x+cw-8,y+150),radius=9,fill='#FFF0C8' if i==model['highlight'] else EMPTY)
            for k,line in enumerate(label.split('\n')): text(d,line,x+cw/2,y+12+k*26,23,INK,True,maxw=cw-12)
            text(d,digit,x+cw/2,y+86,45,TEAL,True)
    if model and model['type']=='line':
        y=740; start,end=model['start'],model['end']
        d.line((220,y,1700,y),fill=MUTED,width=4)
        for i in range(11):
            x=220+148*i; v=start+(end-start)*i/10
            d.line((x,y-12,x,y+12),fill=INK,width=3)
            if i in [0,10]: text(d,f'{v:.{model["decimals"]}f}',x,y+32,32,INK,True)
        if model.get('mark') is not None:
            x=220+1480*(model['mark']-start)/(end-start)
            d.ellipse((x-10,y-10,x+10,y+10),fill=TEAL)
            text(d,str(model['mark']),x,y-62,36,TEAL,True)
    if cue.get('note'): wrapped(d,cue['note'],925,32)
    if cue.get('role')=='question': text(d,'Think time • 4 seconds',W/2,865,36,GOLD,True)
    d.line((90,1000,90+1740*cue.get('lesson_progress',0),1000),fill=TEAL,width=7)
    im.save(path)
