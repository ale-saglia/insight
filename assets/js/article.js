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
})();
