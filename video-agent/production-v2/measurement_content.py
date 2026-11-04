"""Original Year 5 M01/M02 teaching. Reuses the established beat/voice/render schema."""
from content import generic,beat
TOPIC='measurement'
GOALS=[
 ('Measure length accurately using useful metric units.', ['Choose a sensible unit and instrument.','Read a ruler from the correct starting point.','Combine metres and centimetres accurately.']),
 ('Measure mass and capacity using scales and combined units.', ['Distinguish mass from capacity.','Read equal scale intervals.','Combine kilograms and grams or litres and millilitres.']),
 ('Find the perimeter of regular and irregular shapes.', ['Trace the complete outside boundary.','Use matching length units.','Find missing lengths before adding sides.']),
 ('Explain and find area using square units.', ['Cover a surface without gaps or overlaps.','Use rows and columns to count squares.','Distinguish area from perimeter.']),
 ('Solve practical problems with irregular shapes.', ['Split a shape or subtract a missing rectangle.','Check every outside length for perimeter.','Compare designs using the required measure.'])]
def model(kind,**v):return dict(type='measurement',kind=kind,**v)
LESSONS=[]
def add(section,title,opening,concept,examples,question,answer,recap,models,misconception):
 l=generic(TOPIC,section,title,opening,concept,examples,question,answer,recap);i=len(LESSONS);b=l['beats']
 for idx,m in models.items():b[idx]['model']=m
 ch,t,board,m=misconception;w=beat(t,ch,board=board);w['role']='misconception';w['model']=m;b.insert(6,w)
 goal,criteria=GOALS[i];g=beat('Our learning goal is to '+goal[0].lower()+goal[1:],'Today’s Learning Goal',board=[goal]);g['role']='learning_goal';c=beat('Success criteria. I can '+'. I can '.join(s.rstrip('.').lower() for s in criteria)+'.','Success Criteria: I can…',board=[str(j)+'. '+s for j,s in enumerate(criteria,1)]);c['role']='success_criteria';b[1:1]=[g,c]
 b[-1]['text']+=' Reflect on which model helped you and why. Now try the MathMagic practice, and explain your thinking to someone.'
 l['codes']=['AC9M5M01'] if i<2 else ['AC9M5M02'];LESSONS.append(l)

add('lesson1','Choose Units and Measure Length',
 'Could the same pencil seem longer just because someone moved the ruler? Imagine two friends measuring it from different marks. Before we trust a number, let us investigate the unit, the scale and the starting point.',
 'Remember that a measure counts equal units. Millimetres help with small details, centimetres suit a pencil, metres suit a room, and kilometres suit a long journey. Choose a tool with useful markings. Smaller units can give a more precise measurement, rather than changing the object.',
 [('A ribbon begins at the two centimetre mark and ends at nine centimetres. Predict its length. Count the equal one-centimetre intervals between those marks, rather than reading the final label alone.',['Start: 2 cm','End: 9 cm'],
   'There are seven centimetres between the marks. Nine minus two equals seven. Moving the ruler does not stretch the ribbon: subtract the starting reading whenever the object is not lined up with zero.',['9 − 2 = 7 cm','Length is the difference']),
  ('A display board measures two metres and thirty-five centimetres. We want a single centimetre reading. One metre contains one hundred centimetres, so the two metres account for two hundred centimetres.',['1 m = 100 cm','2 m = 200 cm'],
   'Add the remaining thirty-five centimetres. Two hundred plus thirty-five makes two hundred and thirty-five centimetres. The combined measure and the single-unit measure describe exactly the same length.',['200 + 35 = 235 cm','2 m 35 cm = 235 cm'])],
 ('A strip starts at three centimetres and ends at eleven centimetres. How long is it?',['Start 3 cm → end 11 cm','Length = ? cm']),
 ('Eleven minus three is eight centimetres. Check by counting eight equal intervals, or placing a zero-start ruler beside the same strip.',['11 − 3 = 8 cm']),
 'Choose a useful unit, read the interval size and check the starting mark. For a practical investigation, measure a pencil in centimetres and millimetres. Discuss which reading describes its length more precisely.',
 {0:model('ruler',start=2,end=9),1:model('units'),2:model('ruler',start=2,end=9),3:model('ruler',start=2,end=9),4:model('combined',whole=2,part=35,factor=100,big='m',small='cm'),5:model('combined',whole=2,part=35,factor=100,big='m',small='cm'),7:model('ruler',start=3,end=11)},
 ('Read the distance, not just the end','Reading nine centimetres as the ribbon length ignores where it started. Count the space between the marks. A different starting mark changes the subtraction, but not the physical ribbon.',['End reading is not always the length','9 − 2 = 7 cm'],model('ruler',start=2,end=9)))

add('lesson2','Measure Mass and Capacity',
 'A lunchbox feels heavy, while a bottle looks full. Are we measuring the same attribute? Imagine packing for a picnic. We need a balance for mass and a marked container for capacity. Let us choose useful units before measuring.',
 'Mass describes how heavy an object is; capacity describes how much a container can hold. Use grams or kilograms for mass, and millilitres or litres for capacity. One kilogram is one thousand grams. One litre is one thousand millilitres. On every scale, count equal intervals before deciding what one interval represents.',
 [('A bag has a mass of one kilogram and three hundred and fifty grams. Picture one thousand grams as a whole kilogram, with the smaller amount added alongside. What single gram reading would describe the same mass?',['1 kg = 1,000 g','Add another 350 g'],
   'One thousand plus three hundred and fifty is one thousand three hundred and fifty grams. The bag has not become heavier because we changed its name. Kilograms and grams are two units for the same attribute.',['1,000 + 350 = 1,350 g','1 kg 350 g = 1,350 g']),
  ('A jug holds two litres and two hundred and fifty millilitres. Convert the whole litres first. Two groups of one thousand millilitres make two thousand millilitres. Then include the extra marked amount.',['2 L = 2,000 mL','Add another 250 mL'],
   'The capacity is two thousand two hundred and fifty millilitres. On a scale from zero to one thousand with four equal intervals, each interval would be two hundred and fifty millilitres. Count intervals, not just tick marks.',['2,000 + 250 = 2,250 mL','4 equal intervals: 250 mL each'])],
 ('A balance points halfway between five hundred and six hundred grams. What mass does it show?',['500 g → halfway → 600 g','Mass = ? g']),
 ('Halfway is fifty grams beyond five hundred, giving five hundred and fifty grams. The scale is measuring mass, so the answer needs grams, not millilitres.',['500 + 50 = 550 g']),
 'Choose the attribute, unit and instrument together. For a practical challenge, use a kitchen balance or marked jug with an adult. Predict a reading, measure carefully, and explain the difference between your estimate and observation.',
 {0:model('units',attribute='mass-capacity'),1:model('units',attribute='mass-capacity'),2:model('combined',whole=1,part=350,factor=1000,big='kg',small='g'),3:model('combined',whole=1,part=350,factor=1000,big='kg',small='g'),4:model('combined',whole=2,part=250,factor=1000,big='L',small='mL'),5:model('scale',value=2250,maximum=2500,step=250,unit='mL'),7:model('scale',value=550,maximum=1000,step=50,unit='g')},
 ('Match the unit to the attribute','Grams and millilitres are not interchangeable labels. A balance measures mass; a marked jug measures capacity. Equal numerical readings do not make those attributes the same. Read the instrument and include the correct unit.',['Mass: g or kg','Capacity: mL or L'],model('units',attribute='mass-capacity')))

add('lesson3','Trace and Calculate Perimeter',
 'A school garden needs a fence. Would counting the squares inside tell us how much fencing to buy? Imagine walking all the way around its edge. That journey measures the boundary, which is called the perimeter.',
 'Use string to trace a shape, then straighten the string beside a ruler. This makes the idea of perimeter concrete. On a diagram, follow every outside side once and add those lengths using matching units. An inside dividing line is not part of the outside boundary.',
 [('A rectangular garden is seven metres long and four metres wide. Opposite sides have matching lengths. Trace the four edges and predict the total before we add them.',['Opposite sides match','7 m, 4 m, 7 m, 4 m'],
   'Seven plus four plus seven plus four is twenty-two metres. We can also add seven and four, then double eleven. Both methods count the complete boundary exactly once.',['7 + 4 + 7 + 4 = 22 m','2 × (7 + 4) = 22 m']),
  ('Now trace an L-shaped garden. Its top is eight metres and its left side is six. A three-by-two rectangle is missing from the lower right corner. Use subtraction to find the remaining straight lengths.',['Right edge: 6 − 2 = 4 m','Bottom edge: 8 − 3 = 5 m'],
   'The six outside edges measure eight, four, three, two, five and six metres. Their sum is twenty-eight metres. The inward corner still belongs to the outside boundary, so include both of its edges.',['8 + 4 + 3 + 2 + 5 + 6 = 28 m'])],
 ('A rectangle is six metres by three metres. What is its perimeter?',['6 m by 3 m','Perimeter = ? m']),
 ('Six plus three makes nine. Double nine for the four sides: eighteen metres. Check by tracing and adding six, three, six and three.',['2 × (6 + 3) = 18 m']),
 'Perimeter is a length around the complete outside edge. Trace before calculating, find hidden lengths and keep units consistent. Try outlining a book with string, then compare a direct measurement with the total of its side lengths.',
 {0:model('rectangle',w=7,h=4,unit='m',boundary=True),1:model('rectangle',w=7,h=4,unit='m',boundary=True),2:model('rectangle',w=7,h=4,unit='m',boundary=True),3:model('rectangle',w=7,h=4,unit='m',boundary=True),4:model('composite',w=8,h=6,a=3,b=2,unit='m',boundary=True),5:model('composite',w=8,h=6,a=3,b=2,unit='m',boundary=True),7:model('rectangle',w=6,h=3,unit='m',boundary=True)},
 ('Do not multiply for a boundary length','Seven times four counts square units covering this rectangle. It does not measure the fence. For perimeter, trace and add the outside lengths. A useful check is whether your answer has metres or square metres.',['Boundary: add side lengths','Perimeter uses m, not m²'],model('rectangle',w=7,h=4,unit='m',boundary=True)))

add('lesson4','Cover and Calculate Area',
 'How many equal square tiles would cover a small floor? A long piece of string cannot cover the surface. We need a different measure from perimeter: area tells us how much flat space a shape covers.',
 'Arrange equal unit squares without gaps or overlaps. Each square covers one square unit. For a rectangle, equal rows let us count efficiently with multiplication. A square centimetre is a square one centimetre along each side, not a one-centimetre length.',
 [('A rectangle has eight columns and five rows of square-centimetre tiles. Predict how many unit squares cover it. Each row contains eight squares, and there are five equal rows.',['8 squares in each row','5 equal rows'],
   'Five groups of eight make forty unit squares. The area is forty square centimetres. Multiplying eight centimetres by five centimetres counts the same tiled surface, so we write the squared unit.',['8 × 5 = 40 cm²']),
  ('A play mat is seven metres by four metres. Imagine covering it with one-metre squares. There are seven squares along each row, with four rows altogether. What would the surface measurement be?',['7 columns × 4 rows','Each tile: 1 m²'],
   'The area is twenty-eight square metres. The perimeter is a different quantity: seven plus four plus seven plus four is twenty-two metres. Area counts the cover; perimeter measures the border.',['Area: 7 × 4 = 28 m²','Perimeter: 7 + 4 + 7 + 4 = 22 m'])],
 ('A rectangle has six columns and four rows of unit squares. What is its area?',['6 columns × 4 rows','Area = ? square units']),
 ('Four groups of six make twenty-four square units. You can check by counting the tiles or adding six four times. No tile should be counted twice.',['6 × 4 = 24 square units']),
 'Area counts equal squares covering a surface. Use rows and columns to count efficiently and always label the square unit. Draw two rectangles with the same area on squared paper. Do they have to have the same perimeter? Explain with a drawing.',
 {0:model('rectangle',w=8,h=5,unit='cm',grid=True),1:model('rectangle',w=8,h=5,unit='cm',grid=True),2:model('rectangle',w=8,h=5,unit='cm',grid=True),3:model('rectangle',w=8,h=5,unit='cm',grid=True),4:model('rectangle',w=7,h=4,unit='m',grid=True),5:model('rectangle',w=7,h=4,unit='m',grid=True),7:model('rectangle',w=6,h=4,unit='',grid=True)},
 ('Square units are not side lengths','Adding eight and five does not count the tiles covering an eight-by-five rectangle. It counts only two side lengths. To find area, use all five rows of eight equal squares, with no gaps or overlaps.',['5 rows of 8 squares','Area: 40 cm², not 13 cm'],model('rectangle',w=8,h=5,unit='cm',grid=True)))

add('lesson5','Design with Irregular Shapes',
 'A playground has a corner cut out for a tree. Can we still work out how many paving tiles it needs? An irregular outline does not stop us measuring. Let us turn the tricky shape into familiar rectangles.',
 'Build an L shape with square tiles, then slide a pencil along possible dividing lines. You can split its area into non-overlapping rectangles, or start with a large rectangle and subtract the missing part. Both methods must cover exactly the same surface.',
 [('An L-shaped space fits inside an eight-metre by six-metre rectangle. A three-metre by two-metre corner is missing. Predict whether its area is greater or smaller than forty-eight square metres.',['Whole rectangle: 8 × 6 = 48 m²','Missing corner: 3 × 2 = 6 m²'],
   'Subtract the missing six square metres from forty-eight. The L-shaped area is forty-two square metres. As a check, split it into an eight-by-four rectangle and a five-by-two rectangle. Thirty-two plus ten also gives forty-two.',['48 − 6 = 42 m²','8 × 4 + 5 × 2 = 42 m²']),
  ('A larger design fits inside a ten-metre by eight-metre rectangle, with a four-by-three corner missing. Plan the area calculation first. Keep the border measurement separate from the surface measurement.',['Whole area: 10 × 8 = 80 m²','Missing area: 4 × 3 = 12 m²'],
   'The usable area is sixty-eight square metres. For its border, trace ten, five, four, three, six and eight metres. That perimeter is thirty-six metres. Different questions about the same design need different measures.',['Area: 80 − 12 = 68 m²','Border: 10 + 5 + 4 + 3 + 6 + 8 = 36 m'])],
 ('A six-by-five rectangle has a two-by-two corner removed. What area remains?',['Whole: 6 × 5 square units','Remove: 2 × 2 square units']),
 ('Thirty minus four leaves twenty-six square units. The missing corner is not part of the surface, so subtract it once, rather than including the full bounding rectangle.',['30 − 4 = 26 square units']),
 'Choose the measure the problem needs. For area, split or subtract rectangles; for perimeter, trace every outside edge. Draw a garden on squared paper and explain a paving plan and a fencing plan. Check that your answers describe the actual design.',
 {0:model('composite',w=8,h=6,a=3,b=2,unit='m',grid=True),1:model('composite',w=8,h=6,a=3,b=2,unit='m',grid=True),2:model('composite',w=8,h=6,a=3,b=2,unit='m',grid=True),3:model('composite',w=8,h=6,a=3,b=2,unit='m',grid=True),4:model('composite',w=10,h=8,a=4,b=3,unit='m',grid=True),5:model('composite',w=10,h=8,a=4,b=3,unit='m',boundary=True),7:model('composite',w=6,h=5,a=2,b=2,unit='',grid=True)},
 ('The missing corner does not need tiles','Using the full eight-by-six rectangle would include the tree corner. That overcounts six square metres. Subtract the missing rectangle, or add two rectangles that cover only the actual playground.',['48 m² includes the missing corner','48 − 6 = 42 m²'],model('composite',w=8,h=6,a=3,b=2,unit='m',grid=True)))

for lesson in LESSONS:
    for cue in lesson['beats']:
        if cue.get('model'):cue['model']['reveal']=cue['role'] in ['answer','misconception'] or cue['chapter'].endswith(': explain')

# Semantic content must remain visible through the spoken recap, not just a heading.
_RECAPS=[
 ['Choose the unit → read equal intervals.','Length = end reading − start reading.','Try measuring a pencil two ways.'],
 ['Mass: g and kg | Capacity: mL and L','Read intervals; combine matching units.','Predict, measure and explain.'],
 ['Trace every outside edge once.','Add matching length units.','Check by measuring a real boundary.'],
 ['Cover with equal squares, without gaps.','Rows × columns counts area.','Same area need not mean the same perimeter.'],
 ['Area: split or subtract rectangles.','Perimeter: trace the outside boundary.','Plan, calculate and check the real design.']]
for lesson,board in zip(LESSONS,_RECAPS):lesson['beats'][-1]['board']=board
