"""Original Space narration/storyboards, lessons2–10. Review candidates, not releases."""
def lesson(n,title,goal,criteria,hook,body,codes=None):
    beats=[dict(role='opening',chapter='A puzzle to explore',text=hook,board=[],model={'key':'default'}),dict(role='introduction',chapter='Today we are learning',text='Today we are learning to '+goal[0].lower()+goal[1:]+'. We will build an explanation using models, rather than memorising a rule without understanding it.',board=[],model={'key':'default'}),dict(role='learning_goal',chapter='Today’s Learning Goal',text='Our learning goal is to '+goal[0].lower()+goal[1:]+'. As you investigate, connect what you can see, what you can make, and the mathematical language you use.',board=[goal],model={'key':'default'}),dict(role='success_criteria',chapter='Three success criteria',text='First, '+criteria[0]+'. Second, '+criteria[1]+'. Third, '+criteria[2]+'. Keep these goals in mind as you explain each discovery.',board=criteria,model={'key':'default'})]
    for block in body.strip().split('\n\n'):
        heading,speech=block.split('\n',1);role,chapter,key=heading.split('|');beats.append(dict(role=role,chapter=chapter,text=speech.strip(),board=[],model={'key':key}))
    return dict(id='space-lesson'+str(n),topic='space',section='lesson-'+str(n),title=title,beats=beats,codes=codes if codes is not None else ['AC9M5SP01'],enrichment=n==9)

LESSONS=[lesson(2,'Explore Nets','Connect flat nets to three-dimensional objects',['I can match faces and their joins','I can explain a valid cube net','I can explain why a net fails'],
'Imagine a tiny delivery robot that can carry only flat parcels. You need to send it a box for a present. Could you flatten the box, send the pieces still joined, and let the robot rebuild it? Today we will investigate which flat arrangements can become closed objects.',r'''
explanation|Start with a familiar box|net_cross
Think about an empty cardboard box. Open its flaps carefully, then cut along selected edges while keeping the faces connected. When you lay the cardboard flat, you can see regions that used to face different directions. This connected arrangement of faces is called a net.

explanation|A net keeps mathematical information|net_cross
The flat drawing tells us more than the number of faces. It shows the shapes of the faces and which edges remain joined. A fold changes the direction a face points, but does not change its shape or size. Imagine folding along a shared edge like a hinge.

explanation|Build with six squares|net_cross
Use six equal paper squares or imagine six tiles. Put four squares in a vertical row. Attach one square on each side of the second square. Every join is a whole edge. This cross-shaped arrangement is one possible starting point for a cube net.

question|Predict whether the cross closes|net_cross
Choose the square where the side arms meet as the base. Imagine the neighbouring squares lifting around it. Will all six squares cover six different faces, or will two squares try to occupy the same place? Make a prediction and prepare a reason before we reveal the result.

answer|Follow the folds|net_cross
This cross does fold into a cube. The four neighbours around the base become four sides. The remaining square closes the opposite face. The six squares cover six different positions without leaving a missing face. Folding is about where the faces finish, not just how the drawing looks.

explanation|Track opposite faces|net_cross
Label the middle square as the base. The square two steps along the long arm becomes the opposite face. Squares touching the base become its neighbours. Opposite faces do not share an edge on the finished cube, even when a flat net makes their relationship hard to imagine.

explanation|What stays the same?|net_cross
Each face remains the same square during folding. Its four side lengths stay equal and its corners remain right angles. The paper changes direction in space. This is why drawing a smaller square or stretching a face cannot rescue an incorrect arrangement: that would change the intended cube.

explanation|Try a second arrangement|net_t
Now put four equal squares in a horizontal row. Attach one square above the second square and one below that same square. Picture the row wrapping around the four side faces, while the extra squares close the top and bottom. Turning a net on the page does not create a different solid.

explanation|Compare the two drawings|net_t
Our two drawings can look different because the page has been turned. To decide whether they really have different structures, match their whole-edge joins. A rotation or reflection of a working net still folds to a cube. The relationships between the faces matter more than its direction on the table.

question|Will six squares always work?|net_invalid
Here is another arrangement: two rows of three equal squares, making a rectangle. It has six squares, just like the cross. Is the correct face count enough to guarantee a cube? Imagine the folds, and look for faces that would collide or joins that would prevent a proper corner.

answer|Find the obstruction|net_invalid
The rectangle does not fold into a cube. At an interior meeting point, four squares surround the same flat corner. A cube vertex needs three square faces, not four. Trying to fold all these joins cannot produce the required cube corners without cutting an additional join or causing overlap.

misconception|Count and connections both matter|net_invalid
A common mistake is saying, six squares means a cube net. Six equal squares are necessary, but they must also be arranged with the right connections. Count the faces first, then test where they fold. A useful explanation identifies the obstruction instead of simply calling the picture wrong.

explanation|Make a reliable folding test|net_cross
Mark one base square and imagine its neighbours lifting. Keep track of the direction of every new face. If two faces would occupy the same cube position, the arrangement fails. If all six different positions are filled and the joins agree, the arrangement can close into the intended cube.

explanation|Connect nets to drawings|cube
A drawing of the finished cube usually shows only three faces from one viewpoint. The net shows all six. These representations describe the same object in different ways. Use the net to account for hidden faces, rather than assuming an unseen face has disappeared from the solid.

explanation|A different object needs different faces|prism_net
Consider a long rectangular carton. Its faces come in three matching opposite pairs. They need not all be squares. A suitable net uses rectangles whose joining edges have matching lengths. Six equal squares would make a cube, so they would not preserve the dimensions of this longer carton.

explanation|Inspect the joins|prism_net
Before folding, compare the two edges that need to meet. Their lengths must agree. Also check that a closing face has the right shape to fill the opening. A face count alone cannot check dimensions, just as it could not check the square arrangement in our earlier example.

explanation|Independent making challenge|net_cross
Draw or assemble six equal squares in a connected arrangement. Predict whether it will fold before testing a paper model. Record your prediction, the actual result and one reason. If your arrangement fails, change a connection and explain how that change might remove the problem you discovered.

recap|Reflect on the robot’s parcel|net_cross
Our robot can rebuild a box when the flat net preserves the correct faces and joins. You can now connect a net to its solid, test a cube net and explain why some arrangements fail. Choose one valid and one invalid example, and convince a partner using folding evidence.
'''),
lesson(3,'Design and Test Nets','Design and test nets with matching face dimensions',['I can match joining edge lengths','I can build a rectangular-prism net','I can test and improve a design'],
'A toy designer has made a small treasure chest, but the cardboard wrapper will not close. One panel is too short and another flap covers the opening twice. Could you become the packaging engineer who fixes it? Our clues will be face shapes, matching edges and careful testing.',r'''
explanation|Connect to a real package|prism_net
Recall that a net is a connected flat arrangement that folds into an object. Today the faces do not have to be equal squares. Imagine opening a rectangular carton along carefully chosen edges. Opposite faces match, while neighbouring faces may have different dimensions that share just one edge length.

explanation|Choose a precise design|prism_net
We will design a rectangular prism that is four centimetres long, three centimetres wide and two centimetres high. These measurements describe three different directions. Before drawing, point to each direction on an imagined carton. Swapping a height label with a length label would change which panels must meet.

explanation|Identify the face pairs|prism_net
The top and bottom are four by three rectangles. The front and back are four by two rectangles. The two ends are three by two rectangles. This gives three matching pairs and six faces altogether. Notice that each direction appears on more than one face because faces share edges.

explanation|Build the side strip|prism_net
Lay out four side panels in one row. Their widths are four, three, four and three centimetres. Each panel is two centimetres high, so their shared joining edges match. When the row wraps around, the final free edge meets the first free edge to complete the sides.

question|Choose the closing panels|prism_net
The side strip is ready, but the carton still has an opening at the top and bottom. Which pair of rectangles should close those openings? Think about the carton’s length and width, rather than choosing a panel simply because it is available. Predict the dimensions before we continue.

answer|Match the openings|prism_net
We need two four by three rectangles. Attach one above and one below the first four by two side panel. Each attached join is four centimetres long on both faces. The depth of the closing panel is three centimetres, matching the distance across the carton’s opening.

explanation|Check all six faces|prism_net
Our drawing now has four side panels and two closing panels. Trace the boundary and imagine each panel folding to its destination. The two four by three panels become opposite faces. They must not both try to cover the same opening, and the final side-panel seam must still meet.

explanation|Dimensions need a consistent scale|prism_net
Use one grid square for one centimetre when you draw this design. A four-centimetre edge then spans four grid spaces wherever it appears. Keeping one scale lets the picture support the reasoning. Drawing every rectangle as an identical square would hide the important dimensional differences in this example.

misconception|A face count cannot repair a mismatch|prism_bad
Suppose the designer uses a four by two rectangle as the top. There are still six panels, but the top needs a depth of three centimetres. The shorter panel leaves part of the opening uncovered. Adding a label saying top does not change the actual size of the cardboard.

explanation|Change the defective panel|prism_net
Replace that top with a four by three rectangle. Keep the correct side strip and the correct bottom: we do not need to redesign everything. This is a useful engineering habit. Identify the precise mismatch, make the smallest justified correction, and test the altered design again.

explanation|Explore a square-based pyramid|pyramid_net
For a second design, start with a square base. Attach one matching isosceles triangle to each side of the square. Each triangle base must match its square edge. The four triangle tips rise towards one apex when folded, producing a square-based pyramid rather than a prism with two matching ends.

explanation|The triangular faces must agree|pyramid_net
The rising sides of neighbouring triangles must meet when the pyramid closes. Using four matching triangles with suitable height gives a consistent design. Random triangles with the correct base length may still have incompatible side lengths. We need to consider the edges that become joins after folding as well.

question|Count the pyramid’s panels|pyramid_net
Before counting along, predict how many faces belong in this pyramid net. Separate the square base from the triangular side faces. Does the apex need a separate tiny face, or is it a point where existing faces meet? Explain your prediction using the object rather than the drawing alone.

answer|Explain the five faces|pyramid_net
There is one square base and four triangular faces, making five faces altogether. The apex is a vertex, not an extra face. The triangles meet there when folded. This connects our earlier vocabulary about faces and vertices to a practical decision about how many cardboard panels to cut.

explanation|Compare two packaging choices|prism_net
A prism has two matching parallel ends joined by side faces. A pyramid has a base and triangular faces meeting at an apex. Choose a package by considering the object it must contain, then design the appropriate faces. A triangular outline somewhere in a drawing does not identify the whole solid.

explanation|Use a testing record|pyramid_net
Write down the intended object, the number and shape of its faces, and the dimensions of important joining edges. Sketch the net before cutting. After folding, record any gaps or overlaps and where they occur. This turns an unsuccessful trial into useful information for the next version.

explanation|A practical independent challenge|prism_net
Design a different connected net for this same four by three by two centimetre carton. You may change which edges remain joined, but keep every panel at its required dimensions. Predict whether your arrangement will close without overlap, and check all joining edges before making a paper prototype.

explanation|Explain rather than guess|prism_net
For this carton, the opposite face pairs remain four by three, four by two, and three by two centimetres. Rearranging a net changes its connections, not the required faces. Compare your new arrangement with the reference model and explain why its folds should reach the correct positions without gaps or collisions.

recap|Reflect like a designer|prism_net
You can now plan face pairs, match joining edges and test a net against its intended object. Return to the treasure-chest wrapper: what evidence would convince its designer that your correction works? Use a labelled net and a folding explanation, then try a new package of your own.
'''),
lesson(4,'Coordinates and Position','Locate and plot positions using an ordered pair',['I can read the horizontal coordinate first','I can plot a position from an instruction','I can explain why coordinate order matters'],
'A wildlife ranger radios, the missing koala toy is at three, two. Another ranger walks to two, three and finds only a picnic table. Both heard the same numbers! What information must a map provide so that everyone reaches the same place? Let us solve their location mystery.',r'''
explanation|Connect to familiar maps|point32
You may have used rows and columns to find a seat or a square on a game board. A coordinate system also describes positions, but here we locate grid intersections. The axes give two agreed directions, and an ordered pair tells us how far to move along each one.

explanation|Find the shared starting point|origin
The two axes meet at the origin. On our grid its coordinates are zero, zero. The horizontal axis runs to the right, and the vertical axis runs upwards. We are exploring the first quadrant, so the positions we use have non-negative horizontal and vertical coordinates.

explanation|Read the scale carefully|point32
Look at the numbered tick marks before counting. On this grid each interval represents one unit. Count the spaces between marks, not the number of printed labels. The same scale continues across the whole horizontal axis and up the vertical axis, giving a consistent way to locate positions.

explanation|Move horizontally first|point32_x
To find the position three, two, begin at the origin. Move three grid spaces to the right along the horizontal direction. This first coordinate tells us the sideways position. We have not yet used the second coordinate, so we should not stop and claim the position is complete.

explanation|Then move vertically|point32_y
From that horizontal position, move two spaces upwards. Place a point at the intersection you reach. The ordered pair three, two records the complete position. The horizontal-first convention gives both rangers the same instructions, even when they stand on different sides of a printed map.

explanation|Connect the route to the notation|point32
We write the pair in brackets with a comma between the values. The first value is the horizontal coordinate and the second is the vertical coordinate. The pair describes a location, not an addition question. Three and two do not mean that every point five units away will be correct.

question|Predict a new location|point64
Imagine a marker at six, four. Before the point appears, trace the two movements with a finger: six spaces horizontally from the origin, then four vertically. Which intersection should receive the marker? Keep the order clear, and check that you are pointing to an intersection rather than a square centre.

answer|Check six, four|point64
The marker belongs at the intersection six units to the right and four units up from the origin. Read back along horizontal and vertical guide lines to check it. A reliable check uses the axes, rather than remembering only where a dot happened to appear on screen.

explanation|Read a point already plotted|point25
Now reverse the task. Start at the plotted point and trace down to the horizontal axis to read its sideways position: two. Then trace across to the vertical axis to read its height: five. The ordered pair is two, five, because horizontal position is always written first.

misconception|Swapping values changes position|swapped
Two, five and five, two use the same numbers, but they name different points. One is further up; the other is further right. Calling both the same position ignores the agreed order. Compare them with guide lines and explain which coordinate tells you the height in each case.

explanation|A zero coordinate still has meaning|axis04
A point at zero, four sits on the vertical axis. Its horizontal movement from the origin is zero, while its vertical movement is four units. Zero does not mean the position is missing. It gives precise information about a direction in which no movement is needed.

explanation|Compare the other axis|axis40
A point at four, zero sits on the horizontal axis. It is four units to the right, with no upward movement. Compare it with zero, four. These examples show clearly why writing coordinates in the correct order matters, even when one of the values is zero.

explanation|Locate points without a drawn path|point25
As you become confident, you do not need to draw every step from the origin. Use the horizontal and vertical values to imagine guide lines that meet at the target. The drawing method may become quicker, but the meanings of the two coordinates stay exactly the same.

question|Spot the ranger’s error|swapped
A ranger is asked to mark two, five but points to five, two. Before we correct the map, explain the mistake in words. Which movement did the ranger make first, and which movement should have come first? Use a horizontal direction and a vertical direction in your explanation.

answer|Repair the instruction|point25
The ranger swapped the coordinate roles. To mark two, five, move two units right and five units up from the origin. The incorrect marker was five units right and two units up. Both positions are valid grid points, but only one matches the particular instruction we were given.

explanation|Independent plotting challenge|point64
Draw axes from zero to eight using equal one-unit intervals. Plot three positions of your choice and write their coordinates. Ask a partner to plot the same pairs on a separate grid. If the results differ, compare axis labels, scales and coordinate order before deciding who should change a point.

explanation|Describe a useful checking strategy|point32
For each marker, read the coordinates back from the picture without looking at your original instruction. This provides a second way to check the position. You should be able to explain both values: how far across and how far up. A dot without this explanation is only part of the evidence.

recap|Bring the rangers together|point32
Our learning goal was to locate positions using an ordered pair. The rangers can now agree on an origin, scale and horizontal-first convention. You can read, plot and check a point, including positions on an axis. Create one final coordinate clue that leads a friend to exactly one intersection.
''',codes=['AC9M5SP02']),
lesson(5,'Map Routes and Directions','Describe and compare routes on a coordinate grid',['I can follow horizontal and vertical movements','I can connect movements to coordinates','I can compare routes and explain my reasoning'],
'A delivery bicycle must travel from the library to a community garden. One rider turns early and another turns later, but both insist they used the shortest grid route. Can different-looking journeys have the same length? Let us become route planners and check their claims with a map.',r'''
explanation|Start with position and movement|route7
A coordinate pair names a position. A route describes how to travel between positions. These ideas are connected, but they answer different questions. First identify the starting point and destination, then describe each movement clearly enough for another person to follow without watching your finger.

explanation|Agree on map directions|route7
On this map, right means east and up means north. Left means west and down means south. The grid axes still describe horizontal and vertical position. Before using these directions on a real map, check its orientation rather than assuming the top of every page must represent north.

explanation|Read the endpoints|route7
The library is at one, one and the garden is at five, four. To compare the positions, look at each coordinate separately. The horizontal value must increase from one to five. The vertical value must increase from one to four. We can describe these two required changes before choosing turns.

explanation|Model the first journey|route7
From one, one, move four spaces right. The new position is five, one. The vertical coordinate stays one because we have not moved up or down. Then move three spaces up to reach five, four. Each intermediate position gives us a useful check on the directions.

explanation|Record the distance in grid units|route7
This journey uses four horizontal spaces and three vertical spaces, giving seven grid units altogether. We are counting travelled spaces, not the labels at their ends. The turn does not add an extra unit: it changes the direction of the next part of the journey.

question|Try turning first|route7b
What if the second rider goes three spaces north before moving four spaces east? Predict the final position and total grid distance. Think about which coordinate changes during each part. Does changing the order of these two movements change the destination in this particular situation?

answer|Compare both journeys|route7b
The second rider reaches one, four after moving north, then five, four after moving east. The distance is three plus four, also seven grid units. The routes use different intermediate positions but have the same destination and distance. This conclusion follows from the particular movements, not from their appearance.

explanation|Extend to a connected journey|route10
Now the bicycle must continue from the garden at five, four to a gate at seven, four. That adds two spaces east with no vertical change. The complete route uses four right, three up and two right. Keeping a running record helps us avoid forgetting an earlier section.

explanation|Use a movement table|route10
Record the start, each instruction and the new position. After four right, write five, one. After three up, write five, four. After two right, write seven, four. The travelled distance is four plus three plus two, which equals nine grid units for this complete journey.

misconception|Do not add the destination coordinates|route10
A learner adds seven and four and says the journey was eleven units. Those values describe the final position relative to the origin, not the distance travelled from our library. To measure the journey, use the movements along the actual route, including any sections that retrace earlier steps.

explanation|Investigate a detour|detour
Suppose a closed path makes the rider travel one extra space east and then one space back west before continuing. The final destination can remain unchanged, but the rider has travelled two additional grid units. Returning to the same position does not erase the distance already travelled along a detour.

explanation|Distinguish shortest from unique|route7
Among routes restricted to horizontal and vertical grid lines, seven units is a shortest distance from one, one to five, four. Every successful route must cover four units of eastward change and three northward. Different orders can achieve this without backtracking, so shortest does not mean there is only one possible route.

question|Find a missing instruction|missingroute
A walker starts at two, two and ends at six, five. The first instruction is four spaces right. What vertical movement completes the trip? Predict the instruction and explain why it changes only one coordinate. Check the starting height instead of reading the destination’s height as the distance.

answer|Use the change in height|missingroute
After moving right, the walker is at six, two. To reach six, five, move three spaces up. Five minus two gives the required vertical change. Moving five spaces up would reach height seven, because the starting point was already two units above the horizontal axis.

explanation|Include a map scale|scaledroute
Imagine that each grid unit represents ten metres. Our seven-unit library-to-garden route then represents seventy metres along the grid paths. State the scale and units in your answer. A distance of seven grid units is not automatically seven metres unless the map explicitly uses that scale.

explanation|Give directions a partner can check|route7b
Write a new route using at least three instructions and include its start position. Ask a partner to follow it, recording each intermediate coordinate. If the final location is unexpected, compare one instruction at a time. This pinpoints the first disagreement instead of rewriting the whole route by guesswork.

explanation|Independent planning challenge|missingroute
Plan two different shortest grid routes from two, two to six, five. Both need four units of eastward change and three northward, so each can use seven units without backtracking. Explain how their turns differ while the total changes remain the same. Include a labelled sketch as evidence.

recap|Reflect on the riders’ claims|route7
You can now connect positions, movements and travelled distance. Two riders can take different turns yet share a shortest grid distance, while a detour can change distance without changing the destination. Make one final route clue and explain how a coordinate record would help someone check every stage.
''',codes=['AC9M5SP02'])]

LESSONS += [lesson(6,'Translations','Translate a shape while preserving its size and orientation',['I can describe a slide precisely','I can move every vertex by the same amount','I can check what stays unchanged'],
'A theatre crew needs to slide a painted triangle across the stage without turning it. One person moves the top corner further than the others, and suddenly the triangle looks stretched! How could the whole team follow one instruction that keeps the scenery exactly the same shape?',r'''
explanation|Connect to a real slide|translate
Imagine sliding a book across a table while keeping its cover facing the same direction. The book changes position, but you do not turn it over or rotate it. In geometry, a movement of this kind is called a translation. We will describe it precisely on a coordinate grid.

explanation|Track more than one corner|translate
A shape consists of more than its most noticeable corner. Mark each vertex of our triangle and keep the original outline visible. To translate the whole triangle, every vertex must move the same distance in the same direction. The sides connecting those vertices then preserve their lengths and relationships.

explanation|Read the starting positions|translate
Our triangle has vertices at one, one; three, one; and two, three. Read each pair horizontally first, then vertically. These coordinates provide a record of the original position. Before moving anything, point to the base and the upper vertex so you can check whether the final orientation stays the same.

explanation|Give one clear instruction|translate
The stage manager asks for a slide three units right and two units up. This instruction applies to every point of the triangle. It describes the change in position, rather than naming a final coordinate. A point that starts further right will also finish further right than its neighbours.

explanation|Move the first vertex|translate
Begin with the vertex at one, one. Three units right takes its horizontal coordinate to four. Two units up takes its vertical coordinate to three. Its new position is four, three. Mark the corresponding new vertex, and keep the original marker so the movement can be checked.

explanation|Complete the translated triangle|translate
Apply the identical instruction to the other vertices. Three, one becomes six, three. Two, three becomes five, five. Join the new vertices in the same order as the original shape. We now have a translated triangle, not three unrelated dots that happened to move somewhere on the grid.

question|Predict another slide|translate_predict
Return to the original triangle. This time the instruction is two units right and three units up. Where will the vertex at one, one finish? Predict its ordered pair and explain both changes. The original shape remains visible while you think; the translated result has not yet been revealed.

answer|Check the new position|translate_predict
The vertex moves from one, one to three, four. The horizontal coordinate increases by two and the vertical coordinate increases by three. The other original vertices move to five, four and four, six. Check the triangle’s base: it remains horizontal, with the same length as before the slide.

explanation|Describe the unchanged properties|translate
A translation preserves side lengths, angles and orientation. The triangle still points the same way and has the same size. Its location has changed. Compare a pair of corresponding sides, then a pair of corresponding vertices. This is stronger evidence than simply saying the two triangles look rather similar.

misconception|One vertex cannot follow a different rule|translate
Suppose a helper moves one corner four units right while the others move three. That is not the same translation for the whole shape. A connecting side can change length or direction. Correct the corner by applying the same displacement as the other vertices, rather than stretching the outline to make it fit.

explanation|Use a leftward translation|translate_left
For a second worked example, start with vertices four, two; six, two; and five, four. Slide the triangle two units left and one unit up. Moving left reduces the horizontal coordinates, while moving up increases the vertical coordinates. We remain within the first quadrant throughout this example.

explanation|Check all three new pairs|translate_left
Four, two becomes two, three. Six, two becomes four, three. Five, four becomes three, five. Each horizontal value has decreased by two and each vertical value has increased by one. The consistent changes confirm that every vertex followed the same translation instruction, including the upper corner.

explanation|Connect arrows to a movement description|translate_left
Draw an arrow from each original vertex to its matching translated vertex. The arrows have the same direction and length. A single clear arrow can then represent the translation of the whole shape. Explain its horizontal and vertical components so another learner can reproduce the slide without guessing.

question|Can a slide turn a shape?|translate
A classmate says that sliding our triangle across the grid could make its horizontal base become vertical. Is that possible under a translation alone? Predict your answer and give a reason about what happens to the direction of a side. Do not rely only on the triangle’s final location.

answer|Separate a slide from a turn|translate
A translation alone cannot turn the horizontal base vertical. Every point moves by the same displacement, so the direction between two corresponding vertices remains unchanged. Making the base vertical would require a rotation or another transformation. Our precise vocabulary helps us distinguish these different kinds of movement.

explanation|Work backwards to find an instruction|translate
Imagine one vertex moved from one, one to four, three. Compare the coordinates: the horizontal change is three right and the vertical change is two up. Check another corresponding vertex before applying that description to the whole shape. One matching point alone does not prove that all the others moved consistently.

explanation|Independent scenery challenge|translate_left
Draw a small shape with three or four vertices on a grid. Choose a translation that keeps every new vertex within the grid. Record the starting coordinates, instruction and final coordinates. Ask a partner to identify one property that changed and two properties that remained unchanged during your movement.

explanation|Explain the evidence carefully|translate
Useful evidence includes equal corresponding side lengths, unchanged angles and identical displacement arrows. A translation changes the position while preserving the shape’s geometry. If your new picture looks larger, tilted or reversed, investigate which vertex did not follow the instruction. The checking strategy can reveal the specific error.

recap|Reflect on the theatre team|translate
Our scenery team can now move every marked point by one shared instruction. You can describe a translation, plot corresponding vertices and explain why size and orientation stay the same. Finish by giving someone a slide instruction and asking them to justify the result using coordinates and matching arrows.
''',codes=['AC9M5SP03','AC9M5SP02']),
lesson(7,'Reflections','Reflect a shape using equal perpendicular distances from a mirror line',['I can identify a mirror line','I can place matching reflected points','I can explain how a reflection differs from a slide'],
'A designer wants a butterfly decoration with matching wings on either side of a fold. The two wings have the same shape, but sliding one sideways does not make them face each other. What special movement creates a mirror partner? Let us investigate with folds, points and carefully checked distances.',r'''
explanation|Connect to a paper fold|reflect_v
Fold a sheet of paper, place a small ink dot near the fold and imagine pressing it onto the other half. The matching marks lie equally far from the fold on opposite sides. When the paper opens, the crease acts as a mirror line that connects the two positions.

explanation|Identify the line before moving|reflect_v
On our grid, the mirror line is vertical at horizontal coordinate four. Every point on this line has horizontal coordinate four, whatever its height. The line is not itself a side of the triangle. It is the reference that tells us where each matching reflected point must go.

explanation|Use the shortest distance to the line|reflect_v
For this vertical mirror, measure horizontally from the point to the line. That direction meets the line at a right angle. An angled path to some other place on the line is longer and would not give the correct matching position. The reflected point keeps the same vertical coordinate.

explanation|Reflect one vertex|reflect_v
Take the vertex at one, one. It is three units left of the mirror line at four. Its reflected partner must be three units right of that line, at seven, one. Compare the two horizontal distances. They are equal, and the joining segment crosses the mirror at a right angle.

explanation|Reflect the next two vertices|reflect_v
The vertex three, one is one unit left of the line, so it reflects to five, one. The vertex two, three is two units left, so it reflects to six, three. Join the three matching points in their original order. Their positions create the mirror image of the entire triangle.

explanation|Observe what changes and stays|reflect_v
The reflected triangle has the same side lengths and angles as the original. Its facing direction is reversed across the mirror line. It has not simply been slid to a new place. Corresponding points can travel different distances, depending on how far each one started from the mirror.

question|Predict a matching point|reflect_v
Focus on the vertex at two, three and the vertical mirror at four. Before its reflected partner appears, decide how far it is from the line and which side the partner must occupy. Predict the full coordinate pair, including the height, and prepare an equal-distance explanation.

answer|Explain six, three|reflect_v
Two, three is two units left of the mirror. Moving two units to the right of the mirror reaches six, three. The height remains three. The total separation between this point and its partner is four units, but each is only two units from the mirror line itself.

misconception|Do not measure every point from the axis|reflect_v
A common mistake is reflecting across the vertical axis even though the given mirror line is at four. Another is moving every vertex the same sideways distance. Instead, use the specified mirror and measure each point’s own perpendicular distance. A reflection is controlled by the line, not by one shared slide.

explanation|Investigate a horizontal mirror|reflect_h
Now use a horizontal mirror at vertical coordinate four. Measure vertically to this line. The horizontal coordinate stays unchanged because each point and its partner sit directly above and below one another. The equal-distance reasoning is the same, but the direction in which we count has changed.

explanation|Work a horizontal example|reflect_h
The vertex two, one is three units below the mirror, so its partner is two, seven. The vertex four, one reflects to four, seven. The vertex three, three is one unit below the mirror and reflects to three, five. Check each pair against the line instead of swapping the coordinate values.

explanation|Keep coordinate roles separate|reflect_h
Reflecting in a horizontal line does not exchange the two coordinate positions. Each horizontal value remains what it was; the vertical position changes according to distance from the mirror. Reading an ordered pair correctly is still important. A reflection rule does not replace the horizontal-first convention for describing positions.

question|What happens on the mirror?|reflect_on
Consider a point at four, two on our vertical mirror line. Where is its reflected partner? Does it need to move to the other side even though its distance from the mirror is zero? Think about a paper dot placed exactly on a crease, then predict the position.

answer|A point on the line stays put|reflect_on
The point remains at four, two. Its perpendicular distance from the mirror is zero, so the matching distance on the other side is also zero. Points on the mirror line are fixed during the reflection. Other vertices of the same shape may move while that particular vertex stays in place.

explanation|Use a second reflection as a check|reflect_v
Reflect the reflected triangle across the same line again. Each partner returns to the original position, because it travels back to the matching distance on the opposite side. If a second reflection does not restore your starting diagram, check the line, the perpendicular direction and your counting of grid intervals.

explanation|Connect to symmetry without assuming it|reflect_on
A shape can be reflected to a new position even if it has no line of symmetry. A line of symmetry is a special mirror line where the reflected shape matches the original whole outline. Distinguish creating a mirror image from claiming that a particular object is symmetrical about every line.

explanation|Independent butterfly design|reflect_v
Draw a short outline on one side of a vertical grid line. Mark its vertices, count each distance to the line and plot the matching points. Join those partners to make the other wing. Explain how the equal-distance method controls the design more reliably than copying by eye alone.

explanation|Justify and repair a result|reflect_h
To check a proposed reflection, compare corresponding side lengths and inspect the midpoint of each joining segment. That midpoint should lie on the mirror line, with the segment perpendicular to it. You can describe these ideas using counting and right angles, without needing an advanced algebraic rule.

recap|Reflect on the mirrored wings|reflect_v
You can now locate a mirror line, reflect vertices and justify matching positions using equal perpendicular distances. A reflection preserves size while reversing the facing relationship across the mirror. Choose one reflected pair and explain why its coordinates are correct, then challenge a partner with a different mirror line.
''',codes=['AC9M5SP03','AC9M5SP02']),
lesson(8,'Rotations and Symmetry','Rotate shapes about a pivot and investigate rotational symmetry',['I can describe a turn precisely','I can check a rotation using its pivot','I can find an order of rotational symmetry'],
'A playground designer turns a square tile and notices that it sometimes looks exactly as it did before. A long rectangular tile behaves differently. Why do some shapes match their original outline several times during one full turn? Let us investigate turns that move a shape and turns that reveal its symmetry.',r'''
explanation|Connect to familiar turning movements|rotate_ccw
Think about a door turning on a hinge or a clock hand moving around its centre. A rotation needs a fixed pivot. Every point turns through the same angle about that pivot. The shape changes its direction and often its position, while the pivot remains fixed throughout the movement.

explanation|Describe all parts of a turn|rotate_ccw
To give a complete rotation instruction, state the pivot, angle and direction. A quarter turn means ninety degrees. A half turn means one hundred and eighty degrees. Clockwise follows the direction of clock hands, while anticlockwise goes the other way. Leaving out one of these details can make an instruction ambiguous.

explanation|Locate the pivot on the grid|rotate_ccw
Our pivot is at four, four. The outlined shape sits to its right. Choose a marked point on the shape and notice its distance from the pivot. During the turn that point follows a circular path, keeping the same distance from the pivot instead of sliding along a straight route.

explanation|Model a quarter turn anticlockwise|rotate_ccw
Turn the shape ninety degrees anticlockwise around four, four. The part that began to the right of the pivot swings upwards. Keep the original outline as a reference. Every vertex makes the same quarter turn, so the connecting sides and corner angles preserve the original shape’s geometry.

explanation|Check one point numerically|rotate_ccw
Imagine a point at six, four, two units right of the pivot. After the quarter turn anticlockwise, it is two units above the pivot, at four, six. This check uses the pivot’s position as well as the turn. Rotating around the origin would be a different instruction and give a different result.

question|Predict a clockwise quarter turn|rotate_cw
Return to the original shape and keep the pivot at four, four. Where would the point at six, four finish after a ninety-degree clockwise turn? Think of moving from the right-hand direction towards the downward direction. Predict the full coordinates and justify the distance from the pivot.

answer|Check the downward position|rotate_cw
The point finishes at four, two. It is still two units from the pivot, but now directly below it. Compare this with the anticlockwise result four, six. Both turns have the same angle, yet their different directions place the point on opposite sides of the pivot.

misconception|A turn is not a slide|rotate_ccw
A learner moves every vertex three squares right and calls it a quarter turn. That is a translation, not a rotation. A rotation keeps the pivot fixed and changes the directions from it to the vertices. Use the point’s circular path and the changed orientation to explain the difference positively.

explanation|Explore a half turn|rotate_half
Return to the original shape and make a half turn about the same pivot. A point two units right of the pivot moves two units left of it. For a half turn, clockwise and anticlockwise reach the same final position, although the paths travel around different sides along the way.

explanation|Separate a rotation from symmetry|sym_square
Any shape can be rotated, but not every turn makes it match its original outline. Rotational symmetry asks about the special turns where the whole shape fits exactly onto its starting position. Compare every side and corner, rather than accepting a rough resemblance or matching only one particular point.

explanation|Investigate a square|sym_square
Place the pivot at the square’s centre and rotate through one full turn. It matches at ninety, one hundred and eighty, two hundred and seventy, and three hundred and sixty degrees. These four matching positions give the square rotational symmetry of order four. The starting position is not counted a second time.

question|Predict the rectangle’s order|sym_rectangle
Now try a non-square rectangle about its centre. Will a quarter turn match, or do its unequal side lengths prevent that? Predict how many matching positions occur in one full turn, including the final full-turn match. Explain what happens to the long and short sides as it turns.

answer|Explain order two|sym_rectangle
A non-square rectangle matches after a half turn and again after a full turn. A quarter turn exchanges its long-side and short-side directions, so its outline does not fit. It has order two, rather than order four. The requirement is an exact whole-outline match, not simply another rectangular picture.

explanation|Test an equilateral triangle|sym_triangle
An equilateral triangle has three equal sides and three equal angles. About its centre, it matches after turns of one hundred and twenty, two hundred and forty, and three hundred and sixty degrees. That gives order three. The spacing between matching positions is equal throughout the full turn.

explanation|A shape with no smaller matching turn|sym_scalene
A scalene triangle has unequal side lengths. It does not match its starting outline under a smaller positive turn about its centre, but it does match after a complete three-hundred-and-sixty-degree turn. We describe this as order one: there is no non-trivial rotational symmetry to discover before the full turn.

explanation|Connect mirror lines and turns carefully|sym_rectangle
Lines of symmetry and rotational symmetry describe different transformations. A non-square rectangle has mirror lines through the midpoints of opposite sides, and it also has order-two rotational symmetry. Do not assume that seeing a mirror line automatically tells you every matching turn. Test the particular transformation you are asked about.

explanation|Independent tile investigation|sym_square
Choose a paper shape, mark a pivot and trace its original outline. Turn it carefully through one full revolution, recording every exact match after the starting position. State your evidence with an angle or fraction-of-a-turn description in words. Check that the pivot did not drift while you were turning.

explanation|Explain the role of the centre|rotate_half
A shape’s rotational-symmetry investigation normally uses its appropriate centre. A different pivot can move the shape away from the starting outline, even when the angle is a familiar symmetry turn. This is another reason that a complete rotation instruction must name the pivot as well as angle and direction.

recap|Reflect on the playground tiles|sym_square
You can now describe rotations, check a point’s distance from a pivot and investigate exact matching turns. The square, non-square rectangle and equilateral triangle have different rotational orders for mathematical reasons. Choose a new tile shape and predict its order, then test the whole outline before accepting your prediction.
''',codes=['AC9M5SP03','AC9M5SP02']),
lesson(9,'Classification Algorithms','Build and test branching decisions that classify shapes',['I can choose defining properties','I can follow a yes-or-no decision path','I can repair a rule using a counterexample'],
'A museum robot has mixed up the shape labels. It calls every four-sided figure a square and every object with a square face a square too! Could you teach it to ask better questions? We will design decisions that use evidence, then test them on shapes that challenge a tempting rule.',r'''
explanation|Connect to decisions you already make|class_square
You use decisions when sorting objects: is it flat, does it roll, or does it have straight sides? A classification algorithm makes the questions explicit so another person can follow the same process. Each answer sends the object along a branch towards an appropriately justified group or label.

explanation|Choose mathematical properties|class_square
Colour and direction on a page do not define a square. A square has four equal sides and four right angles. These properties remain true when it is turned. Begin with features that matter mathematically, rather than choosing a question that works only because of how one example was drawn.

explanation|State which objects the rule covers|class_square
Our first decision tree is for quadrilaterals: flat shapes with four straight sides. State that starting group clearly. A test designed for these shapes should not silently be applied to cylinders or triangles. Knowing the input group helps us decide whether a sequence of questions is complete and meaningful.

explanation|Ask about right angles|class_square
The first question is, does the quadrilateral have four right angles? A yes answer sends it towards the rectangle family. A no answer sends it down a different branch. This first decision does not yet distinguish a square from a non-square rectangle, because both have four right angles.

explanation|Add a second useful test|class_square
For a shape on the yes branch, ask whether all four sides are equal. If yes, the shape is a square. If no, it is a non-square rectangle. Each extra question should separate cases that the earlier question could not distinguish, instead of repeating information we already know.

question|Predict the square’s path|class_square
A quadrilateral has four right angles and four equal sides. Follow the two questions silently before its final group is shown. Which branch should it take at each decision? Prepare a complete explanation, including why the first answer alone would not identify its most specific label.

answer|Explain both yes decisions|class_square
It answers yes to four right angles and yes to four equal sides, so the most specific label on our tree is square. It also belongs to the rectangle family. Giving a more specific label does not erase the broader family properties that helped us reach the decision.

explanation|Try a non-square rectangle|class_rectangle
A rectangle that is longer than it is wide still has four right angles. It follows the first yes branch. Its four sides are not all equal, so the next answer is no. The tree identifies a non-square rectangle while keeping its relationship with squares clear and mathematically accurate.

misconception|Four equal sides are not enough|class_rhombus
The museum robot’s tempting rule says that four equal sides always mean square. A non-square rhombus is a counterexample: it has four equal sides but does not have four right angles. One genuine counterexample is enough to disprove an always claim, even if many earlier examples seemed to support it.

explanation|Follow the other branch|class_rhombus
For a quadrilateral without four right angles, we can still ask whether all four sides are equal. If yes, the most specific group here is a non-square rhombus. If no, we need other quadrilateral descriptions. The meaning of an answer depends on the earlier decisions along that particular path.

explanation|Use inclusive mathematical families|class_square
A square is also a rectangle and a rhombus: it has the defining properties of both. Our decision tree can give one most-specific label for a task while explaining these overlapping families. Avoid a rule claiming that a square can never be a rectangle simply because the words are different.

question|Repair the robot’s rule|class_rhombus
The robot asks only whether all four sides are equal, then labels every yes answer square. Which additional property should it check? Predict a repair that correctly handles both a square and a non-square rhombus. Choose evidence about the shape, rather than changing its colour or orientation on the screen.

answer|Add an angle decision|class_square
The robot must also check for four right angles. Together with four equal sides, this identifies a square. A four-equal-sided shape without four right angles belongs to a different most-specific group. Test the repaired rule on both examples to show that the added decision solves the original problem.

explanation|Keep solids separate from flat shapes|class_cube
Now change the input group to three-dimensional objects. A cube is not a square, even though each of its faces is square. Ask first whether the exhibit is a solid object or a flat shape. Words such as faces and edges describe different features from the sides of a flat quadrilateral.

explanation|Make a solid-object branch|class_cube
Within our familiar solid objects, six square faces arranged as a closed cube identify a cube. A non-cube rectangular prism also has six faces, but they are not all squares. Face count alone cannot distinguish these examples. The algorithm needs both the relevant shapes of faces and their connections.

explanation|Test more than the favourite example|class_rectangle
Make a test set containing a square, a long rectangle, a non-square rhombus and another quadrilateral. Turn the drawings and change their sizes. The classification should remain stable because those changes preserve the defining properties. If a label changes only because the picture was tilted, the decision rule needs repair.

explanation|Independent museum challenge|class_cube
Write a short yes-or-no pathway for a small collection of objects you can describe accurately. Include at least one pair that shares a property but needs different labels. Ask a partner to follow your decisions exactly, then use any unexpected outcome to identify a missing or ambiguous question.

explanation|Explain why the rule works|class_rhombus
A useful justification describes the input group, every decision and the evidence for each answer. It also explains what a label means. An algorithm is more than a decorative diagram with arrows: its questions must lead suitable objects to defensible groups, including the difficult examples chosen to challenge it.

recap|Reflect on the robot’s improved thinking|class_square
You can now choose defining properties, follow branching decisions and improve a rule using a counterexample. This investigation extends our shape reasoning and careful use of mathematical vocabulary. Give the museum robot one final test case, predict its full path, and explain why every decision is justified.
''',codes=[]),
lesson(10,'Integrated Spatial Design Challenge','Combine nets, coordinates and transformations in a justified design',['I can connect a net to a model','I can locate and transform a display','I can check and explain a complete spatial plan'],
'Your class is designing a miniature discovery museum. The model buildings must fold from cardboard, visitors need a reliable map, and a pair of displays must have a planned relationship. Can you connect several geometry ideas into one design that another team could actually build and check?',r'''
explanation|Break the design into decisions|prism_net
Before drawing a polished plan, identify what each representation will tell you. A net describes the faces and joins of a model building. A coordinate map records positions. Transformations describe precise changes to a display shape. Each representation answers a different question, so we should not expect one drawing to replace all the others.

explanation|Choose a buildable building model|prism_net
Our first building is a rectangular prism measuring four by three by two centimetres. Use the matching opposite-face pairs from our net investigation. The top and bottom are four by three, the long sides four by two, and the ends three by two. Check both sizes and connections before folding.

explanation|Check a second model|pyramid_net
A square-based pyramid can mark the information point. Its net needs one square base and four suitable matching triangular faces. It is not a triangular prism: the triangular sides meet at an apex rather than connecting two matching parallel ends. Explain that structural difference to the team constructing the model.

explanation|Set up a shared map|route7
Choose one origin, label the axes and use equal one-unit intervals. Our entrance is at one, one and the main exhibit is at five, four. These pairs specify positions, not journeys. Every team must use the same horizontal-first convention, or the museum labels could point visitors towards the wrong places.

explanation|Work a visitor route|route7
From the entrance at one, one, move four grid spaces right to five, one. Then move three spaces up to five, four. The route uses seven grid units. Record the turn as well as the destination so that another team can follow the instructions without needing to copy your finger movements.

question|Predict a different shortest route|route7b
Could a visitor travel north first and still reach the main exhibit in seven grid units? Predict the intermediate coordinate after the first movement, then the final coordinate. Explain why a different-looking route can have the same length when it uses the same horizontal and vertical changes without backtracking.

answer|Verify both coordinates and distance|route7b
Moving three units north first reaches one, four. Moving four units east then reaches five, four. Three plus four still gives seven grid units. The intermediate location differs from our first route, while the destination and total distance agree. State each of these comparisons separately rather than calling the routes identical.

explanation|Design a translated display|design_translate
Our triangular display has vertices at one, two; two, two; and one, three. We want a matching display four units right and one unit up. Apply this instruction to every vertex. A translation preserves side lengths, angles and orientation, so no corner should follow its own different movement.

explanation|Check the translated coordinates|design_translate
The new vertices are five, three; six, three; and five, four. Compare each pair of corresponding positions. Every horizontal value increased by four and every vertical value increased by one. Join the new vertices in order, and keep the original outline so the unchanged geometry remains easy to inspect.

misconception|A similar-looking sketch is not evidence|design_translate
One team redraws the triangle larger because it looks more impressive on the map. That may be a design choice, but it is not the requested translation. The instruction requires the same size and shape. Correct the individual vertex positions using the shared movement, rather than stretching a side by eye.

explanation|Add a reflected partner|design_reflect
Now reflect the translated triangle across the vertical line at horizontal coordinate four. Its vertex five, three is one unit right of that line, so its partner is three, three. The vertex six, three is two units right and reflects to two, three. Check each distance independently.

explanation|Complete the mirror relationship|design_reflect
The remaining vertex five, four reflects to three, four. All matching pairs keep their vertical coordinates and lie equally far from the mirror on opposite sides. This movement reverses their facing relationship while preserving size. It is different from the earlier slide, which used one shared displacement without reversing the orientation.

question|Predict a point on the mirror|reflect_on
A decorative marker lies at four, two, directly on the same vertical mirror line. Where will its reflected partner be? Predict whether it moves at all, and explain your answer using distance from the line. This is a useful boundary case for checking whether our reflection reasoning is consistent.

answer|Use the zero-distance case|reflect_on
The marker remains at four, two. Its distance from the mirror is zero, so the matching point on the other side is still the same position. A reflection can keep points on its mirror fixed while moving other points. Do not force every point to travel simply because a transformation was requested.

explanation|Choose a rotating sign|sym_square
For a square direction sign, investigate a full turn about its centre. It matches its original outline four times, including the final full-turn match. That is order-four rotational symmetry. A non-square rectangular sign has order two. The different side relationships explain why their exact matching turns differ.

explanation|Explain object labels carefully|class_cube
The museum labels must distinguish flat face shapes from whole objects. A square face belongs to a cube, but a cube is not itself a square. Use faces, edges and vertices to describe solids, and appropriate side-and-angle properties for flat shapes. Precise vocabulary makes the model instructions easier to follow.

explanation|Independent design challenge|exit_route
Plan a small visitor route starting at two, two. Move three units right and two units up. Work out the endpoint, then add an original shape and a translated partner elsewhere on the grid. Include a suitable building net and explain at least one check for each part of your design.

explanation|Check the route and the whole plan|exit_route
The visitor finishes at five, four: the horizontal coordinate increases by three and the vertical coordinate by two. Now inspect your other choices. Are net edges compatible? Do translated vertices share one movement? Are reflected points equally far from the specified line? A complete design needs evidence for every mathematical decision.

recap|Reflect on a design someone can build|route7
You have connected flat nets, solid models, coordinate locations, routes and transformations. Return to the learning goal and explain which representation solved each design problem. Share one convincing check and one improvement you made after testing. Your final plan should help another team understand not just what to build, but why it works.
''',codes=['AC9M5SP01','AC9M5SP02','AC9M5SP03'])]
