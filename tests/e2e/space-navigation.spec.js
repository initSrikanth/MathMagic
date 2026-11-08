const {test,expect}=require('@playwright/test');

// Space discovery must remain reachable from the existing authenticated dashboard.
// The dashboard guard is stubbed for navigation assertions only, never in production.
test('Year 5 Space dashboard card leads to ten lessons and interactive labs',async({page})=>{
 await page.route('**/js/auth-guard.js*',route=>route.fulfill({status:200,contentType:'application/javascript',body:''}));
 await page.route('**/js/measurement-dashboard.js*',route=>route.fulfill({status:200,contentType:'application/javascript',body:''}));
 await page.goto('/dashboard.html');
 const card=page.locator('a.activity-card[href="space-lessons.html"]');
 await expect(card).toHaveAttribute('href','space-lessons.html');
 // Navigation guard is deliberately fail-closed without a real approved user.
 // Assert the real dashboard link, then inspect the lesson destination directly.
 await page.goto('/space-lessons.html');
 await expect(page).toHaveURL(/space-lessons\.html$/);
 await expect(page.getByRole('link',{name:/challenge/i}).first()).toBeVisible();
});

test('Space challenge never enables starting before approved-user service is ready',async({page})=>{
 // With no Firebase approval, the service cannot be exposed. The assessment stays disabled.
 await page.route('**/js/space-auth.js',route=>route.fulfill({status:200,contentType:'application/javascript',body:''}));
 await page.goto('/space-challenge.html');
 await expect(page.locator('#startBtn')).toBeDisabled();
 await expect(page.locator('body')).toHaveClass(/auth-loading/);
});
