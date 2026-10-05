const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync('functions/index.js','utf8');
assert(src.includes('enforceAppCheck:true'),'App Check enforcement missing');
assert(src.includes("db.doc('access/'+uid)"),'server approval check missing');
assert(src.includes("d.uid!==req.auth.uid"),'session ownership check missing');
assert(src.includes('const {answer,solution,...safe}=q'),'answer stripping missing');
assert(!/return\{sessionId:id,question:q/.test(src),'raw question may expose answer');
assert(src.includes("throw new HttpsError('unauthenticated'"),'auth rejection missing');
console.log('Protected Fractions architecture static checks passed');
