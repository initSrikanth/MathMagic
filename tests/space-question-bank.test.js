/* Independent Year 5 Space assessment mathematical checks. Run: node tests/space-question-bank.test.js */
'use strict';
const assert=require('node:assert/strict');
const {generate}=require('../js/space-question-bank.js');
const curriculum=new Set(['AC9M5SP01','AC9M5SP02','AC9M5SP03','AC9M5SP04']);
const parsePair=s=>{const m=/^\((-?\d+),(-?\d+)\)$/.exec(s);return m&&m.slice(1).map(Number)};
let inspected=0;
for(let seed=1;seed<=1000;seed++){
 const questions=generate(seed);assert.equal(questions.length,30);assert.equal(new Set(questions.map(q=>q.stem)).size,30);
 const descriptors=new Set();
 for(const [i,q] of questions.entries()){
  assert.equal(q.band,Math.floor(i/5)+1);assert.equal(q.options.length,4);assert.equal(new Set(q.options).size,4);
  assert(q.options.includes(q.answer));assert(q.explanation.length>20);assert(curriculum.has(q.descriptor));descriptors.add(q.descriptor);
  let m;
  if((m=/point is (\d+) units right and (\d+) units up/.exec(q.stem))){assert.equal(q.answer,`(${m[1]},${m[2]})`)}
  else if((m=/Translate the point \((\d+),(\d+)\) (\d+) units to the right/.exec(q.stem))){assert.deepEqual(parsePair(q.answer),[+m[1]+ +m[3],+m[2]])}
  else if((m=/Reflect \((\d+),(\d+)\) in the vertical line x = (\d+)/.exec(q.stem))){assert.deepEqual(parsePair(q.answer),[2* +m[3]- +m[1],+m[2]])}
  else if((m=/closed polygon with exactly (\d+) straight sides/.exec(q.stem))){assert.equal(q.answer,({3:'triangle',4:'quadrilateral',5:'pentagon',6:'hexagon',7:'heptagon'})[m[1]])}
  else if(q.stem.includes('rotated 90° anticlockwise')){assert.deepEqual(parsePair(q.answer),[3,2])}
  else if(q.stem.includes('robot starts at (3,2)')){assert.deepEqual(parsePair(q.answer),[5,5])}
  else if(q.stem.includes('square logo')){assert.equal(q.answer,'90°')}
  else if(q.stem.includes('2-by-3 rectangle')){assert(q.answer.startsWith('No,'))}
  else if(q.stem.includes('sorting algorithm first asks')){assert(q.answer.includes('edges equal'))}
  else if(q.stem.startsWith('How many ')){const oracle={'cube|faces':6,'triangular prism|vertices':6,'square-based pyramid|faces':5,'rectangular prism|edges':12,'triangular prism|faces':5};const parts=/How many (faces|edges|vertices) does a (.*?) have/.exec(q.stem);assert(parts);assert.equal(Number(q.answer),oracle[parts[2]+'|'+parts[1]])}
  else throw Error('Unvalidated question family: '+q.stem);
  inspected++;
 }
 assert.deepEqual([...descriptors].sort(),[...curriculum].sort());
}
console.log('PASS: '+inspected+' questions across 1,000 seeds; 30 unique per seed; four descriptors; independent arithmetic and classification checks.');
