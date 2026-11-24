'use strict';
// Planning/release eligibility only; never reads or modifies pupil progress.
function strandReady(matrix, navigation, name) {
  const strand=navigation.strands.find(s=>s.name===name);
  const rows=matrix.descriptors.filter(r=>r.strand===name);
  return Boolean(strand && rows.length && rows.every(r=>r.status==='COMPLETE') &&
    strand.development_status==='COMPLETE' && strand.media_status==='APPROVED' && strand.qa_status==='PASS' &&
    strand.deployment_status==='VERIFIED_LIVE' && strand.service_status==='VERIFIED');
}
function canStartStrand(matrix,navigation,name) {
  const index=matrix.development_order.indexOf(name);
  return index>=0 && matrix.development_order.slice(0,index).every(s=>strandReady(matrix,navigation,s));
}
function canStartYear6(matrix,navigation) {
  return matrix.development_order.length===6 && matrix.development_order.every(s=>strandReady(matrix,navigation,s));
}
module.exports={strandReady,canStartStrand,canStartYear6};
