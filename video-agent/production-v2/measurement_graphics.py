"""Metric instruments and equal-unit geometric models, drawn without external art."""
import math

def draw_model(d,m,progress):
    from graphics import text,INK,TEAL,GOLD,EMPTY
    kind=m['kind']
    if kind=='units':
        mass=m.get('attribute')=='mass-capacity'
        data=[('g','Mass: paperclip'),('kg','Mass: packed bag'),('mL','Capacity: small bottle'),('L','Capacity: large jug')] if mass else [('mm','Small details'),('cm','Pencil length'),('m','Room length'),('km','Long journey')]
        text(d,'Choose the attribute, unit and instrument',960,515,40,INK,True)
        for i,(unit,example) in enumerate(data):
            x=220+i*380;d.rounded_rectangle((x,600,x+350,800),radius=20,fill=EMPTY if i%2==0 else '#FFF1D0',outline=TEAL,width=3)
            text(d,unit,x+175,625,65,TEAL,True);text(d,example,x+175,735,30,INK,True,maxw=330)
        text(d,'Equal scale intervals support an accurate reading.',960,875,36,INK,True)
    elif kind=='ruler':
        left=260;right=1660;y=610;maximum=max(12,m['end']+1);span=(right-left)/maximum
        d.rounded_rectangle((left-20,y-40,right+20,y+100),radius=12,fill='#FFF1D0',outline=INK,width=3)
        for i in range(maximum+1):
            x=left+i*span;d.line((x,y,x,y+45),fill=INK,width=3);text(d,str(i),x,y+55,34,INK,True)
            if i<maximum:
                for j in range(1,10):d.line((x+j*span/10,y,x+j*span/10,y+(27 if j==5 else 15)),fill=INK,width=1)
        a=left+m['start']*span;b=left+m['end']*span
        d.rounded_rectangle((a,y-95,a+(b-a)*progress,y-58),radius=8,fill=TEAL)
        for x in [a,b]:d.line((x,y-55,x,y+5),fill=TEAL,width=5)
        text(d,'Centimetres (each small interval is 1 mm)',960,790,37,INK,True)
        text(d,('Length: '+str(m['end']-m['start'])+' cm') if m['reveal'] else 'Length: count the space between the end marks',960,875,39,TEAL,True)
    elif kind=='combined':
        whole=m['whole'];part=m['part'];factor=m['factor'];big=m['big'];small=m['small'];start=960-((whole+1)*390-60)/2
        for i in range(whole):
            x=start+i*390;d.rounded_rectangle((x,580,x+330,780),radius=18,fill=EMPTY,outline=TEAL,width=3)
            text(d,'1 '+big,x+165,600,50,TEAL,True);text(d,str(factor)+' '+small,x+165,705,42,INK,True)
        x=start+whole*390;d.rounded_rectangle((x,580,x+330,780),radius=18,fill='#FFF1D0',outline=GOLD,width=3);text(d,str(part)+' '+small,x+165,650,48,INK,True)
        text(d,'Same amount, renamed in one unit',960,505,40,INK,True)
        text(d,'Total: '+(str(whole*factor+part)+' '+small if m['reveal'] else '? '+small),960,875,46,TEAL,True)
    elif kind=='scale':
        maximum=m['maximum'];step=m['step'];value=m['value'];left=340;right=1580;y=665
        d.line((left,y,right,y),fill=INK,width=6)
        for i in range(maximum//step+1):
            v=i*step;x=left+(right-left)*v/maximum;major=maximum//step<=10 or i%5==0 or v==maximum
            d.line((x,y-20,x,y+(35 if major else 20)),fill=INK,width=3)
            if major:text(d,str(v),x,y+55,34,INK,True)
        x=left+(right-left)*value/maximum;d.polygon([(x,y-10),(x-18,y-55),(x+18,y-55)],fill=TEAL)
        text(d,'Equal intervals: '+str(step)+' '+m['unit'],960,520,42,INK,True)
        text(d,'Reading: '+(str(value)+' '+m['unit'] if m['reveal'] else '? '+m['unit']),960,840,44,TEAL,True)
    else:
        w=m['w'];h=m['h'];a=m.get('a',0);b=m.get('b',0);scale=min(1400/w,365/h);left=960-w*scale/2;top=535;unit=m['unit']
        points=[(0,0),(w,0),(w,h-b),(w-a,h-b),(w-a,h),(0,h)] if kind=='composite' else [(0,0),(w,0),(w,h),(0,h)]
        xy=lambda x,y:(left+x*scale,top+y*scale)
        d.polygon([xy(x,y) for x,y in points],fill=EMPTY)
        if m.get('grid'):
            for row in range(h):
                for col in range(w):
                    if kind=='composite' and col>=w-a and row>=h-b:continue
                    x,y=xy(col,row);d.rectangle((x,y,x+scale,y+scale),fill=TEAL if row*w+col<w*h*progress else EMPTY,outline='white',width=2)
        outline=[xy(x,y) for x,y in points+[points[0]]]
        d.line(outline,fill=INK,width=3,joint='curve')
        if m.get('boundary'):
            remaining=sum(math.dist(a,b) for a,b in zip(outline,outline[1:]))*progress
            for a1,b1 in zip(outline,outline[1:]):
                length=math.dist(a1,b1);ratio=min(1,max(0,remaining/length)) if length else 0
                if ratio:d.line((a1,(a1[0]+(b1[0]-a1[0])*ratio,a1[1]+(b1[1]-a1[1])*ratio)),fill=GOLD,width=8)
                remaining-=length
            text(d,str(h-b)+' '+unit,left+w*scale+85,top+(h-b)*scale/2,36,INK,True)
            text(d,str(w-a)+' '+unit,left+(w-a)*scale/2,top+h*scale+15,36,INK,True)
        text(d,str(w)+' '+unit,960,480,42,INK,True);text(d,str(h)+' '+unit,left-90,top+h*scale/2,40,INK,True)
        if kind=='composite':
            # Dashed outline identifies the missing corner without filling it.
            x1,y1=xy(w-a,h-b);x2,y2=xy(w,h)
            for x in range(round(x1),round(x2),18):d.line((x,y2,min(x+9,x2),y2),fill=GOLD,width=2)
            for y in range(round(y1),round(y2),18):d.line((x2,y,x2,min(y+9,y2)),fill=GOLD,width=2)
            text(d,str(a)+' '+unit,(x1+x2)/2,y1+10,36,INK,True);text(d,str(b)+' '+unit,x1+85,(y1+y2)/2,36,INK,True)
        if not m.get('boundary'):
            text(d,'Equal unit squares; no gaps or overlaps' if m.get('grid') else 'Equal side units',960,955,32,INK,True)
