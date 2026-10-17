const { test, expect } = require('@playwright/test');
async function openTopic(page){await page.route('**/js/whole-numbers-auth.js*',r=>r.abort());await page.goto('/whole-numbers.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'))}
test('whole numbers lessons render',async({page})=>{await openTopic(page);for(const id of ['lesson1','lesson2','lesson3','lesson4','lesson5','challenge']){await page.locator('[data-screen="'+id+'"]').click();await expect(page.locator('#'+id)).toHaveClass(/active/)}});
test('whole numbers 30 question challenge',async({page})=>{await openTopic(page);await page.locator('[data-screen="challenge"]').click();for(let q=1;q<=30;q++){await expect(page.locator('#qNumber')).toHaveText(q+' / 30');await expect(page.locator('#qPrompt')).not.toBeEmpty();const choices=page.locator('#qAnswer [data-choice]');if(await choices.count())await choices.first().click();else{await page.locator('#qAnswer input').fill('999999');await page.locator('#checkAnswer').click()}await expect(page.locator('#qFeedback')).not.toBeEmpty();await expect(page.locator('#nextQuestion')).toBeEnabled();await page.locator('#nextQuestion').click()}await expect(page.locator('#resultCard')).toContainText('CHALLENGE COMPLETE')});

test('all five lessons retain only their corresponding MathMagic video at desktop tablet and mobile sizes',async({page})=>{
  await openTopic(page);
  const sources=[
    'MathMagic_Understanding_Place_Value_1080p.mp4',
    'MathMagic_Expanded_Form_1080p.mp4',
    'MathMagic_Comparing_Ordering_Whole_Numbers_1080p.mp4',
    'MathMagic_Decimal_Place_Value_1080p.mp4',
    'MathMagic_Comparing_Ordering_Locating_Decimals_1080p.mp4'
  ];
  await expect(page.locator('iframe, a[href*="youtube"]')).toHaveCount(0);
  await expect(page.locator('body')).not.toContainText('Math Antics');
  for(const width of [1440,768,390]){
    await page.setViewportSize({width,height:900});
    for(let i=0;i<sources.length;i++){
      const id='lesson'+(i+1);
      await page.locator('[data-screen="'+id+'"]').click();
      const lesson=page.locator('#'+id),card=lesson.locator('.video-resource');
      await expect(card).toHaveCount(1);
      await expect(card).toHaveClass(/mathmagic-owned-video/);
      const video=card.locator('video');
      await expect(video).toBeVisible();
      await expect(video).toHaveAttribute('controls','');
      await expect(video).toHaveAttribute('playsinline','');
      await expect(video).toHaveAttribute('preload','metadata');
      await expect(video.locator('source')).toHaveAttribute('src','videos/'+sources[i]);
      await expect(card.locator('a.resource-link')).toHaveAttribute('href','videos/'+sources[i]);
      await expect(video.locator('track')).toHaveAttribute('src','videos/'+sources[i].replace('.mp4','.vtt'));
      await expect(card.locator('details')).toContainText('video transcript');
      expect(await video.evaluate(el=>{
        const r=el.getBoundingClientRect(),p=el.closest('.video-frame').getBoundingClientRect();
        return r.width>0 && r.height>0 && r.left>=p.left-1 && r.right<=p.right+1 &&
          Math.abs(r.width/r.height-16/9)<0.03 &&
          document.documentElement.scrollWidth<=window.innerWidth;
      })).toBe(true);
      expect(await card.evaluate(el=>el.nextElementSibling.classList.contains('lesson-nav'))).toBe(true);
    }
  }
});

test('whole numbers generator stress: 500 full challenges preserve structure and answers',async({page})=>{
 await openTopic(page);
 const report=await page.evaluate(()=>{
  const failures=[],seen=new Set(),levels=['FOUNDATION','DEVELOPING','DEVELOPING +','PROFICIENT','APPLICATION','CHALLENGE'];
  for(let run=0;run<500;run++){
   const quiz=window.MathMagicWholeNumbersQA.buildQuiz();
   if(quiz.length!==30)failures.push('count '+quiz.length);
   for(let band=0;band<6;band++)for(let i=band*5;i<band*5+5;i++)if(quiz[i].level!==levels[band])failures.push('band '+i);
   for(const q of quiz){
    if(!q.prompt||q.answer==null||String(q.answer).trim()==='')failures.push('missing answer');
    if(q.type==='choice'){
     if(!q.options.includes(q.answer))failures.push('answer missing:'+q.topic);
     if(new Set(q.options).size!==q.options.length)failures.push('duplicate option:'+q.topic);
    }
   }
   seen.add(quiz.map(q=>q.prompt+'|'+q.display+'|'+q.answer).join('||'));
  }
  return{failures:failures.slice(0,20),distinct:seen.size};
 });
 expect(report.failures).toEqual([]);expect(report.distinct).toBeGreaterThan(450);
});
test('whole numbers progress uses the 30-question scale',async({page})=>{
 await openTopic(page);
 const src=await (await page.request.get('/js/whole-numbers-auth.js')).text();
 expect(src).toContain('p.bestScore+"/30"');
 expect(src).toContain('Number(score)===30');
 expect(src).not.toContain('bestScore+"/20"');
});
