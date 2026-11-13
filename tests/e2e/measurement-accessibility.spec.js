const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
// Axe checks supplement genuine listening, practical pedagogy and physical-device review.
// Firebase is isolated only for UI inspection, never bypassed by the production page.
test('Measurement WCAG AA, keyboard focus and lesson media accessibility',async({page})=>{
 await page.route('**/js/measurement-auth.js*',r=>r.fulfill({contentType:'application/javascript',body:"document.body.classList.remove('auth-loading');window.MathMagicMeasurementProgress={saveAttempt:async()=>({attempts:1,bestScore:30})};"}));
 await page.goto('/measurement.html');
 for(const screen of ['lesson1','lesson2','lesson3','lesson4','lesson5','challenge']){
  await page.locator('[data-screen="'+screen+'"]').click();
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  expect(results.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),screen).toEqual([]);
  const active=page.locator('#'+screen);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  if(screen!=='challenge'){
   const v=active.locator('video');await expect(v.locator('track[kind="captions"]')).toHaveCount(1);await expect(v).toHaveAttribute('aria-label',/.+/);
   await v.focus();await expect(v).toBeFocused();await expect(active.locator('summary')).toBeVisible();
  }
 }
 await page.keyboard.press('Tab');
 await page.locator('[data-screen="lesson1"]').focus();
 expect(await page.locator('[data-screen="lesson1"]').evaluate(el=>getComputedStyle(el).outlineStyle)).not.toBe('none');
});
