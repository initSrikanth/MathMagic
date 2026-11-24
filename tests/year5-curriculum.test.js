'use strict';
const fs=require('fs'),crypto=require('crypto'),assert=require('node:assert/strict');
const matrix=require('../docs/year5/curriculum-coverage.json'),nav=require('../docs/year5/strand-topics.json'),audit=require('../docs/year5/resource-audit.json');
const {strandReady,canStartStrand,canStartYear6}=require('../tools/curriculum/gates');
const counts={Number:['N',10],Algebra:['A',2],Measurement:['M',4],Space:['SP',3],Statistics:['ST',3],Probability:['P',2]};
const expected=Object.entries(counts).flatMap(([strand,[code,n]])=>Array.from({length:n},(_,i)=>['AC9M5'+code+String(i+1).padStart(2,'0'),strand]));
assert.equal(matrix.descriptors.length,24);assert.equal(new Set(matrix.descriptors.map(r=>r.code)).size,24);
function target(href){const[path,hash]=href.split('#');const file=path.split('?')[0];assert.ok(fs.existsSync(file),href);if(hash)assert.ok(fs.readFileSync(file,'utf8').includes('id="'+hash.split('~')[0]+'"'),href);}
for(const[code,strand]of expected){
 const r=matrix.descriptors.find(r=>r.code===code);assert.ok(r,code);assert.equal(r.strand,strand);
 assert.ok(['COMPLETE','PARTIAL','MISSING','UNVERIFIED'].includes(r.status));assert.ok(r.description.length>65);
 assert.ok(r.required_knowledge_and_skills.length>=2);assert.equal(r.skill_evidence.length,r.required_knowledge_and_skills.length);
 assert.ok(r.development_status&&r.deployment_status&&r.corrective_action.length&&r.achievement_standard_aspect);
 for(const ref of r.lessons)target(ref);
 if(r.status==='COMPLETE'){
  assert.equal(r.gaps.length,0,code);assert.ok(r.lessons.length&&r.interactive_activity&&r.assessment&&r.video_coverage.length,code);
  for(const skill of r.skill_evidence){assert.equal(skill.verification,'IMPLEMENTED');assert.ok(skill.references.length);for(const ref of skill.references)target(ref);}
 }
 if(['PARTIAL','MISSING'].includes(r.status))assert.ok(r.gaps.length,code);
 if(r.interactive_activity)target(r.interactive_activity.path);
 if(r.assessment){target(r.assessment.path);const source=fs.readFileSync(r.assessment.path,'utf8');for(const symbol of r.assessment.symbols)assert.ok(source.includes(symbol),code+': '+symbol);for(const t of r.assessment.validation)target(t);}
 for(const video of r.video_coverage){target(video.path);assert.match(video.sha256,/^[a-f0-9]{64}$/);assert.ok(video.approval_status&&video.approval_evidence);target(video.approval_evidence);}
}
assert.equal(audit.pages.length,10);assert.equal(audit.pages.reduce((n,p)=>n+p.videos.length,0),56);
for(const asset of audit.assets)assert.equal(crypto.createHash('sha256').update(fs.readFileSync(asset.path)).digest('hex'),asset.sha256,asset.path);
assert.equal(audit.live.length,217);assert.ok(audit.live.every(r=>r.matches_local&&r.sha256));
const approvedStats=require('../video-agent/statistics/checkpoint.json');
for(const video of approvedStats.lessons){const recorded=audit.assets.find(a=>a.path===video.video);assert.ok(recorded);assert.equal(recorded.sha256,video.bundle_sha256.video);}
assert.deepEqual(nav.enabled_years,[5]);assert.deepEqual(nav.supported_year_range,[1,10]);assert.equal(nav.strands.length,6);
for(const s of nav.strands){
 target('year5-'+s.id+'.html');assert.ok(counts[s.name]);
 for(const t of s.topics){for(const code of t.codes)assert.ok(matrix.descriptors.some(r=>r.code===code&&r.strand===s.name));for(const l of t.lessons){target(l.href);target(l.activity);}target(t.assessment);}
 const html=fs.readFileSync('year5-'+s.id+'.html','utf8');assert.ok(html.includes('js/auth-guard.js?v=6'));assert.ok(!/AC9M5(?:N|A|M|SP|ST|P)\d/.test(html),'Internal codes leaked to children');assert.equal(strandReady(matrix,nav,s.name),false);
}
assert.equal(canStartStrand(matrix,nav,'Number'),true);for(const s of ['Algebra','Measurement','Space','Statistics','Probability'])assert.equal(canStartStrand(matrix,nav,s),false);
assert.equal(canStartYear6(matrix,nav),false);assert.equal(matrix.year6_allowed,false);
// Completing coverage alone never grants media/service/deployment clearance.
const complete=structuredClone(matrix);complete.descriptors.forEach(r=>r.status='COMPLETE');assert.equal(canStartYear6(complete,nav),false);
const released=structuredClone(nav);released.strands.forEach(s=>Object.assign(s,{media_status:'APPROVED',qa_status:'PASS',deployment_status:'VERIFIED_LIVE',service_status:'VERIFIED'}));
assert.equal(canStartYear6(complete,released),true);released.strands[2].media_status='REVIEW_REQUIRED';assert.equal(canStartYear6(complete,released),false);released.strands[2].media_status='APPROVED';released.strands[0].service_status='UNVERIFIED';assert.equal(canStartStrand(complete,released,'Algebra'),false);
console.log('PASS: 24 descriptor records, exact strand/code counts, lesson/tool/assessment links, 207 preserved asset hashes, 217 recorded live matches, six protected strand routes and fail-closed sequential/year-level completion gates.');
