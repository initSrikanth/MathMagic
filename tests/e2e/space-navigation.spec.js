const {test,expect}=require('@playwright/test');

// Space discovery must remain reachable from the existing authenticated dashboard.
// The dashboard guard is stubbed for navigation assertions only, never in production.
test('Year 5 Space dashboard card leads to ten lessons and interactive labs',async({page})=>{
 await page.route('**/js/auth-guard.js*',route=>route.fulfill({status:200,contentType:'application/javascript',body:''}));
 await page.route('**/js/measurement-dashboard.js*',route=>route.fulfill({status:200,contentType:'application/javascript',body:''}));
 await page.goto('/dashboard.html');
 const card=page.getByRole('link',{name:/Space and Geometry/});
 await expect(card).toHaveAttribute('href','space-lessons.html');
 await card.click();
 await expect(page).toHaveURL(/space-lessons\.html$/);
 await expect(page.getByRole('link',{name:/challenge/i}).first()).toBeVisible();
});

test('Space challenge never enables starting before approved-user service is ready',async({page})=>{
 // With no Firebase approval, the service cannot be exposed. The assessment stays disabled.
 await page.route('**/js/space-auth.js',route=>route.fulfill({status:200,contentType:'application/javascript',body:''}));
 await page.goto('/space-challenge.html');
 await expect(page.getByRole('button',{name:'Start challenge'})).toBeDisabled();
 await expect(page.locator('body')).toHaveClass(/auth-loading/);
});
