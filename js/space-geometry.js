/* Exact geometry helpers shared by Space tools and assessment; no authentication changes. */
(function(root){'use strict';
const translate=(p,dx,dy)=>[p[0]+dx,p[1]+dy];
const reflect=(p,axis,k)=>axis==='x'?[2*k-p[0],p[1]]:[p[0],2*k-p[1]];
function rotate(p,c,turns){let x=p[0]-c[0],y=p[1]-c[1];for(let i=0;i<((turns%4)+4)%4;i++)[x,y]=[-y,x];return[x+c[0],y+c[1]]}
function cubeNet(cells){
 const key=p=>p.join(','),neg=a=>a.map(x=>-x),same=(a,b)=>a.every((x,i)=>x===b[i]);
 const lookup=new Set(cells.map(key));if(cells.length!==6||lookup.size!==6)return{valid:false,reason:'Choose exactly six distinct squares.'};
 const frames=new Map([[key(cells[0]),{u:[1,0,0],v:[0,1,0],n:[0,0,1]}]]),queue=[cells[0]];
 const neighbour=(f,dx,dy)=>dx===1?{u:neg(f.n),v:f.v,n:f.u}:dx===-1?{u:f.n,v:f.v,n:neg(f.u)}:dy===1?{u:f.u,v:neg(f.n),n:f.v}:{u:f.u,v:f.n,n:neg(f.v)};
 for(let i=0;i<queue.length;i++){const p=queue[i],f=frames.get(key(p));for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const q=[p[0]+dx,p[1]+dy],k=key(q);if(!lookup.has(k))continue;const expected=neighbour(f,dx,dy);if(frames.has(k)){const actual=frames.get(k);if(!['u','v','n'].every(a=>same(actual[a],expected[a])))return{valid:false,reason:'These joined edges demand incompatible folds.'}}else{frames.set(k,expected);queue.push(q)}}}
 if(frames.size!==6)return{valid:false,reason:'All six squares must be connected edge to edge.'};
 if(new Set([...frames.values()].map(f=>key(f.n))).size!==6)return{valid:false,reason:'Two squares would cover the same cube face.'};
 const opposite=[];for(let i=0;i<cells.length;i++)for(let j=i+1;j<cells.length;j++)if(same(frames.get(key(cells[i])).n,neg(frames.get(key(cells[j])).n)))opposite.push([i,j]);return{valid:true,reason:'Each square folds to a distinct cube face.',opposite,frames:Object.fromEntries(frames)};
}
const api={translate,reflect,rotate,cubeNet};root.SpaceGeometry=api;if(typeof module!=='undefined')module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
