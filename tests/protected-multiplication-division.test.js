const fs=require('fs'),assert=require('assert'),s=fs.readFileSync('functions/index.js','utf8'),client=fs.readFileSync('js/multiplication-division.js','utf8');
assert(s.includes('startMultiplicationDivisionChallenge=onCall({enforceAppCheck:true}'));
assert(s.includes('submitMultiplicationDivisionAnswer=onCall({enforceAppCheck:true}'));
assert(s.includes("if(!(await approved(req.auth.uid)))"));
assert(s.includes("d.topic!=='multiplication-division'"));
const mdSubmit=s.slice(s.indexOf('exports.submitMultiplicationDivisionAnswer'));
assert(!mdSubmit.includes('answer:ok?null:k.answer'));
assert(mdSubmit.includes('solution:ok?null:k.solution,score,complete'));

assert(s.includes('function publicMD(q,i){const{answer,solution,...safe}=q'));
assert(s.includes('mdDecimalQuotient'));
assert(s.includes('mdFractionQuotient'));
assert(s.includes("'choice'"));
assert(!client.includes('function mult1('));
assert(!client.includes('function mult2('));
assert(!client.includes('buildQuiz'));
assert(!client.includes('using local UI QA generator'));
assert(client.includes("throw new Error('Protected service unavailable')"));
console.log('Protected Multiplication & Division architecture and fail-closed checks passed');
