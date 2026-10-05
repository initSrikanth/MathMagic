const {test,expect}=require('@playwright/test');
async function openTopic(page){await page.route('**/js/decimals-percentages-auth.js*',r=>r.abort());await page.goto('/decimals-percentages.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'))}
test('five lessons and privacy-enhanced resources',async({page})=>{await openTopic(page);for(const id of ['place','compare','percent','connect','apply']){await page.locator('[data-screen="'+id+'"]').click();await expect(page.locator('#'+id)).toBeVisible()}const frames=page.locator('.video-resource iframe');await expect(frames).toHaveCount(2);for(let i=0;i<2;i++){await expect(frames.nth(i)).toHaveAttribute('src',/^https:\/\/www\.youtube-nocookie\.com\/embed\//);await expect(frames.nth(i)).toHaveAttribute('title',/.+/);await expect(frames.nth(i)).toHaveAttribute('loading','lazy')}await expect(page.locator('.video-resource a.resource-link')).toHaveCount(2)});
test('complete 30-question challenge flow',async({page})=>{await openTopic(page);await page.locator('[data-screen="challenge"]').click();for(let q=1;q<=30;q++){await expect(page.locator('#qNumber')).toHaveText(q+' / 30');await expect(page.locator('#qPrompt')).not.toHaveText('');const choices=page.locator('#qAnswer [data-choice]');if(await choices.count())await choices.first().click();else{await page.locator('#answerInput').fill('999');await page.locator('#checkAnswer').click()}await expect(page.locator('#qFeedback')).not.toHaveText('');await expect(page.locator('#nextQuestion')).toBeEnabled();await page.locator('#nextQuestion').click()}await expect(page.locator('#resultCard')).toContainText('CHALLENGE COMPLETE')});
test('Year 5 boundary excludes percentage-of-quantity examples',async({page})=>{await openTopic(page);const text=await page.locator('body').innerText();expect(text).not.toMatch(/60% of 40|25% of 80|percentage discount/i)});

test('generator stress: 500 full challenges preserve structure, answers and notation',async({page})=>{
 await openTopic(page);
 const report=await page.evaluate(()=>{
  const failures=[],seen=new Set(),levels=['FOUNDATION','DEVELOPING','DEVELOPING +','PROFICIENT','APPLICATION','CHALLENGE'];
  for(let run=0;run<500;run++){
   const quiz=window.MathMagicDecimalsQA.buildQuiz();
   if(quiz.length!==30)failures.push('count '+quiz.length);
   for(let band=0;band<6;band++)for(let i=band*5;i<band*5+5;i++)if(quiz[i].level!==levels[band])failures.push('band '+i);
   for(const q of quiz){
    if(!q.prompt||q.answer==null)failures.push('missing');
    if(q.type==='choice'){
     if(!q.options.includes(q.answer))failures.push('answer missing');
     if(new Set(q.options).size!==q.options.length)failures.push('duplicate option:'+q.topic+':'+q.options.join(' || '));
    }
    const visible=[q.prompt,q.display,...(q.options||[])].join(' ').replace(/<[^>]*>/g,' ');
    const sm=visible.match(/\b\d+\s*\/\s*\d+\b/);if(sm)failures.push('slash fraction:'+q.topic+':'+sm[0]+':'+visible);
   }
   seen.add(quiz.map(q=>q.prompt+'|'+q.display+'|'+q.answer).join('||'));
  }
  return {failures:failures.slice(0,20),distinct:seen.size};
 });
 expect(report.failures).toEqual([]);expect(report.distinct).toBeGreaterThan(450);
});
test('incorrect feedback and final result use 30-question scale',async({page})=>{
 await openTopic(page);await page.locator('[data-screen="challenge"]').click();
 for(let q=1;q<=30;q++){const choices=page.locator('#qAnswer [data-choice]');if(await choices.count())await choices.first().click();else{await page.locator('#answerInput').fill('999');await page.locator('#checkAnswer').click()}await expect(page.locator('#qFeedback')).not.toHaveText('');await page.locator('#nextQuestion').click()}
 await expect(page.locator('#resultCard')).toContainText('out of 30 correct');
});
