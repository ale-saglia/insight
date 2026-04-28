(function() {
  const nav = document.getElementById('site-nav');
  const domainsGroup = document.querySelector('.domains-group');
  const domainsDropdown = document.querySelector('.domains-dropdown');
  const domainsDropdownTrigger = document.querySelector('.domains-dropdown-trigger');
  const domainsDropdownMenu = document.querySelector('.domains-dropdown-menu');

  if (!nav || !domainsGroup || !domainsDropdown || !domainsDropdownTrigger || !domainsDropdownMenu) return;

  let lastExpanded = null;
  let requiredWidth = null;
  let isCalculatingWidth = false;

  function calculateRequiredWidth() {
    if (isCalculatingWidth) return;
    isCalculatingWidth = true;
    try {
      const wasHidden = domainsGroup.classList.contains('hidden');
      domainsGroup.classList.remove('hidden');
      const prevWrap = nav.style.flexWrap;
      nav.style.flexWrap = 'nowrap';
      requiredWidth = nav.scrollWidth;
      nav.style.flexWrap = prevWrap;
      if (wasHidden) domainsGroup.classList.add('hidden');
    } finally {
      isCalculatingWidth = false;
    }
  }

  function checkLayout() {
    const navWidth = nav.clientWidth;
    if (requiredWidth === null) calculateRequiredWidth();
    const shouldExpand = navWidth >= requiredWidth;
    if (lastExpanded === shouldExpand) return;
    lastExpanded = shouldExpand;
    if (shouldExpand) {
      domainsGroup.classList.remove('hidden');
      domainsDropdown.classList.remove('visible');
      domainsDropdownMenu.classList.remove('open');
      domainsDropdownTrigger.setAttribute('aria-expanded', 'false');
    } else {
      domainsGroup.classList.add('hidden');
      domainsDropdown.classList.add('visible');
    }
    nav.style.visibility = '';
  }

  domainsDropdownTrigger.addEventListener('click', function(e) {
    e.preventDefault();
    domainsDropdownMenu.classList.toggle('open');
    domainsDropdownTrigger.setAttribute('aria-expanded',
      domainsDropdownMenu.classList.contains('open') ? 'true' : 'false');
  });

  document.addEventListener('click', function(e) {
    if (!domainsDropdown.contains(e.target)) {
      domainsDropdownMenu.classList.remove('open');
      domainsDropdownTrigger.setAttribute('aria-expanded', 'false');
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && domainsDropdownMenu.classList.contains('open')) {
      domainsDropdownMenu.classList.remove('open');
      domainsDropdownTrigger.setAttribute('aria-expanded', 'false');
      domainsDropdownTrigger.focus();
    }
  });

  Array.from(domainsDropdownMenu.querySelectorAll('a')).forEach(function(link) {
    link.addEventListener('click', function() {
      domainsDropdownMenu.classList.remove('open');
      domainsDropdownTrigger.setAttribute('aria-expanded', 'false');
    });
  });

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function() { checkLayout(); });
  } else {
    setTimeout(checkLayout, 100);
  }

  const ro = new ResizeObserver(checkLayout);
  ro.observe(nav);
})();
