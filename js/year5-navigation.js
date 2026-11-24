/* Presentation only. Keep the existing topic, authentication and progress services. */
(() => {
  'use strict';
  const courses = {
    'whole-numbers.html': ['number', 'Whole Numbers & Place Value'],
    'fractions.html': ['number', 'Fractions'],
    'decimals-percentages.html': ['number', 'Decimals & Percentages'],
    'addition-subtraction.html': ['number', 'Addition & Subtraction'],
    'multiplication-division.html': ['number', 'Multiplication & Division'],
    'factors-multiples.html': ['number', 'Factors & Multiples'],
    'measurement.html': ['measurement', 'Measuring Our World'],
    'time-angles.html': ['measurement', 'Time and Angles'],
    'space-lessons.html': ['space', 'Space and Geometry'],
    'space-lab.html': ['space', 'Space and Geometry'],
    'space-net-explorer.html': ['space', 'Space and Geometry'],
    'space-coordinates.html': ['space', 'Space and Geometry'],
    'space-symmetry.html': ['space', 'Space and Geometry'],
    'space-classification.html': ['space', 'Space and Geometry'],
    'space-challenge.html': ['space', 'Space and Geometry'],
    'statistics.html': ['statistics', window.StatisticsConfig?.title || 'Data Detectives — Statistics']
  };
  const page = location.pathname.split('/').pop();
  const course = courses[page];
  if (!course) return;
  const main = document.querySelector('main');
  if (!main) return;
  const strand = page === 'multiplication-division.html' && new URLSearchParams(location.search).get('strand') === 'algebra' ? 'algebra' : course[0];
  const nav = document.createElement('nav');
  nav.className = 'curriculum-nav';
  nav.setAttribute('aria-label', 'Curriculum breadcrumb');
  const list = document.createElement('ol');
  for (const [label, href] of [['Year 5', 'dashboard.html'], [strand[0].toUpperCase() + strand.slice(1), 'year5-' + strand + '.html'], [course[1], null]]) {
    const li = document.createElement('li');
    if (href) {
      const a = document.createElement('a'); a.href = href; a.textContent = label; li.append(a);
    } else { li.textContent = label; li.setAttribute('aria-current', 'page'); }
    list.append(li);
  }
  nav.append(list); main.before(nav);

  // Legacy tabbed courses did not open hidden panels from fragment links.
  // Use their actual click handler, including assessment initialisation.
  function followFragment() {
    let fragment;
    try { fragment = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const [id, activity] = fragment.split('~');
    if (!id) return;
    const target = document.getElementById(id);
    const tab = [...document.querySelectorAll('[data-screen]')].find(t => t.dataset.screen === id);
    if (!target || !tab) return;
    tab.click();
    if (activity === 'activity') {
      const tool = target.querySelector('.tool, .measurement-interactive, .practice');
      const focus = tool?.querySelector('input, select, textarea, button') || target.querySelector('input, select, textarea');
      if (focus) { focus.focus({preventScroll: true}); focus.scrollIntoView({block: 'center'}); }
    }
  }
  window.addEventListener('hashchange', followFragment);
  followFragment();
})();
