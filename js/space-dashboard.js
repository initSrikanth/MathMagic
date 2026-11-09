// Update only Space cards; preserve the existing dashboard auth guard and other topic cards.
import {initializeApp,getApps,getApp} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js';
import {getAuth,onAuthStateChanged} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js';
import {getFirestore,doc,getDoc} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js';
import {firebaseConfig} from './firebase-config.js';

const app=getApps().length?getApp():initializeApp(firebaseConfig);
const auth=getAuth(app),db=getFirestore(app);
const TOPICS=['space','time-angles'];

function paint(card,progress={}){
  const attempts=Math.max(0,Number(progress.attempts)||0);
  const completed=Math.min(5,Math.floor(attempts));
  const best=Math.max(0,Math.min(30,Number(progress.bestScore)||0));
  const dots=card.querySelector('.practice-dots');
  const count=card.querySelector('[data-attempts]');
  const bar=card.querySelector('[data-progress-bar]');
  const score=card.querySelector('[data-best]');
  const badge=card.querySelector('[data-proficiency]');
  if(dots)dots.textContent=Array.from({length:5},(_,i)=>i<completed?'●':'○').join(' ');
  if(count)count.textContent=completed+'/5';
  if(bar)bar.style.width=completed*20+'%';
  if(score)score.textContent=attempts?'Best: '+best+'/30':'Best: —';
  if(badge)badge.textContent=progress.proficient===true?'✓ PROFICIENT':attempts?'IN PROGRESS':'START';
}

onAuthStateChanged(auth,async user=>{
  if(!user)return;
  const cards=TOPICS.map(topic=>({topic,card:document.querySelector('[data-topic-progress="'+topic+'"]')})).filter(item=>item.card);
  if(!cards.length)return;
  try{
    const access=await getDoc(doc(db,'access',user.uid));
    if(auth.currentUser?.uid!==user.uid||!(access.exists()&&access.data().approved===true))return;
    await Promise.all(cards.map(async({topic,card})=>{
      try{
        const snap=await getDoc(doc(db,'progress',user.uid,'topics',topic));
        if(auth.currentUser?.uid===user.uid)paint(card,snap.exists()?snap.data():{});
      }catch(error){console.warn('Space progress unavailable for '+topic,error)}
    }));
  }catch(error){console.warn('Space access check unavailable; dashboard access guard remains authoritative.',error)}
});
