(function() {
  const backLink = document.getElementById('back-link');
  const topLink = document.getElementById('top-link');
  const referrer = document.referrer;
  const currentDomain = window.location.hostname;

  let internalReferrerPath = null;
  if (referrer) {
    try {
      const referrerUrl = new URL(referrer);
      if (referrerUrl.hostname === currentDomain && referrerUrl.pathname !== '/') {
        internalReferrerPath = referrerUrl.pathname;
        backLink.style.display = 'inline-block';
      }
    } catch (e) {}
  }

  window.addEventListener('scroll', function() {
    topLink.style.display = window.scrollY > 400 ? 'inline-block' : 'none';
  });

  backLink.addEventListener('click', function(e) {
    if (internalReferrerPath) { e.preventDefault(); history.back(); }
  });

  topLink.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  const sourceRefs = document.querySelectorAll('.source-ref');
  let openSourceRef = null;

  if (sourceRefs.length) {
    document.documentElement.classList.add('source-popovers-ready');
  }

  function getSourcePopover(ref) {
    if (!ref) { return null; }
    return ref._sourcePopover || ref.querySelector('.source-popover');
  }

  function positionSourcePopover(ref) {
    const popover = getSourcePopover(ref);
    if (!popover) { return; }

    const margin = 12;
    const gap = 8;
    const viewportWidth = document.documentElement.clientWidth || window.innerWidth;
    const viewportHeight = window.innerHeight;
    const refRect = ref.getBoundingClientRect();

    popover.classList.add('source-popover-portal');
    popover.style.left = '0px';
    popover.style.top = '0px';
    popover.style.width = window.innerWidth <= 700 ? `${Math.max(0, viewportWidth - (margin * 2))}px` : '';

    const popoverRect = popover.getBoundingClientRect();
    const width = Math.min(popoverRect.width, viewportWidth - (margin * 2));
    const minLeft = window.scrollX + margin;
    const maxLeft = window.scrollX + viewportWidth - width - margin;
    const preferredLeft = window.scrollX + refRect.left + (refRect.width / 2) - (width / 2);
    const left = Math.min(Math.max(preferredLeft, minLeft), maxLeft);

    let top = window.scrollY + refRect.bottom + gap;
    if (refRect.bottom + gap + popoverRect.height > viewportHeight && refRect.top - popoverRect.height - gap > margin) {
      top = window.scrollY + refRect.top - popoverRect.height - gap;
    }

    popover.style.left = `${left}px`;
    popover.style.top = `${top}px`;
  }

  function setSourcePopoverOpen(ref, isOpen) {
    const trigger = ref.querySelector('.source-ref-trigger');
    const popover = getSourcePopover(ref);

    ref.classList.toggle('is-open', isOpen);
    if (trigger) {
      trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }
    if (popover) {
      popover.classList.toggle('is-open', isOpen);
    }
  }

  function closeSourcePopover(ref) {
    const popover = getSourcePopover(ref);
    if (!ref) { return; }

    setSourcePopoverOpen(ref, false);
    if (popover && popover.parentNode !== ref) {
      popover.classList.remove('source-popover-portal');
      popover.removeAttribute('style');
      ref.appendChild(popover);
    }
    if (openSourceRef === ref) {
      openSourceRef = null;
    }
  }

  function openSourcePopover(ref) {
    const popover = getSourcePopover(ref);
    if (!popover) { return; }

    if (openSourceRef && openSourceRef !== ref) {
      closeSourcePopover(openSourceRef);
    }

    openSourceRef = ref;
    if (popover.parentNode !== document.body) {
      document.body.appendChild(popover);
    }
    setSourcePopoverOpen(ref, true);
    positionSourcePopover(ref);
  }

  function closeOpenSourcePopover() {
    closeSourcePopover(openSourceRef);
  }

  function refOrPopoverContainsFocus(ref) {
    const popover = getSourcePopover(ref);
    return ref.contains(document.activeElement) || (popover && popover.contains(document.activeElement));
  }

  function scheduleSourcePopoverClose(ref) {
    window.setTimeout(function() {
      const popover = getSourcePopover(ref);
      const pointerInside = ref.matches(':hover') || (popover && popover.matches(':hover'));
      if (!pointerInside && !refOrPopoverContainsFocus(ref)) {
        closeSourcePopover(ref);
      }
    }, 80);
  }

  sourceRefs.forEach(function(ref) {
    const trigger = ref.querySelector('.source-ref-trigger');
    const popover = ref.querySelector('.source-popover');
    ref._sourcePopover = popover;

    ref.addEventListener('mouseenter', function() { openSourcePopover(ref); });
    ref.addEventListener('mouseleave', function() { scheduleSourcePopoverClose(ref); });
    ref.addEventListener('focusin', function() { openSourcePopover(ref); });
    ref.addEventListener('focusout', function() { scheduleSourcePopoverClose(ref); });

    if (popover) {
      popover.addEventListener('mouseleave', function() { scheduleSourcePopoverClose(ref); });
      popover.addEventListener('focusout', function() { scheduleSourcePopoverClose(ref); });
    }

    if (trigger) {
      trigger.addEventListener('click', function(e) {
        e.stopPropagation();
        openSourcePopover(ref);
      });
    }
  });

  document.addEventListener('click', function(e) {
    const popover = getSourcePopover(openSourceRef);
    if (openSourceRef && !openSourceRef.contains(e.target) && !(popover && popover.contains(e.target))) {
      closeOpenSourcePopover();
    }
  });

  window.addEventListener('resize', function() {
    if (openSourceRef) {
      positionSourcePopover(openSourceRef);
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeOpenSourcePopover();
    }
  });

})();
