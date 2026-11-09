// Course presentation only; authentication, practice and progress keep their existing modules.
(() => {
  'use strict';
  const tabs = [...document.querySelectorAll('[role="tab"][data-screen]')];
  if (!tabs.length) return;
  const panels = tabs.map(tab => document.getElementById(tab.dataset.screen));

  function show(id, {focusHeading = false, updateHistory = false} = {}) {
    const selected = tabs.findIndex(tab => tab.dataset.screen === id);
    if (selected < 0) return false;
    tabs.forEach((tab, index) => {
      const active = index === selected;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      panels[index].classList.toggle('active', active);
      panels[index].hidden = !active;
      if (!active) panels[index].querySelectorAll('video').forEach(video => video.pause());
    });
    if (updateHistory && location.hash !== '#' + id) history.pushState(null, '', '#' + id);
    // Keep the selected tab in the mobile strip without moving the page vertically.
    const strip = tabs[selected].parentElement;
    const tab = tabs[selected];
    if (strip.scrollWidth > strip.clientWidth) {
      const left = tab.offsetLeft;
      if (left < strip.scrollLeft) strip.scrollLeft = left;
      else if (left + tab.offsetWidth > strip.scrollLeft + strip.clientWidth)
        strip.scrollLeft = left + tab.offsetWidth - strip.clientWidth;
    }
    if (focusHeading) panels[selected].querySelector('h2').focus();
    return true;
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => show(tab.dataset.screen, {updateHistory: true}));
    tab.addEventListener('keydown', event => {
      const targets = {ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length,
        Home: 0, End: tabs.length - 1};
      if (!(event.key in targets)) return;
      event.preventDefault();
      const next = tabs[targets[event.key]];
      show(next.dataset.screen, {updateHistory: true});
      next.focus();
    });
  });
  document.querySelectorAll('[data-lesson-next]').forEach(button => button.addEventListener('click', () => {
    show(button.dataset.lessonNext, {focusHeading: true, updateHistory: true});
  }));
  const restore = () => show(location.hash.slice(1)) || show('lesson-1');
  window.addEventListener('hashchange', restore);
  window.addEventListener('popstate', restore);
  restore();
})();
