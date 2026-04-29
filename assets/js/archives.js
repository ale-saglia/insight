const searchInput = document.getElementById('search-input');
const items = document.querySelectorAll('.search-item');
const yearHeadings = document.querySelectorAll('.archive-year');
const filterBtns = document.querySelectorAll('.filter-btn');
const keywordBtns = document.querySelectorAll('.keyword-btn');
const keywordFiltersContainer = document.getElementById('keyword-filters');
const noResultsMessage = document.getElementById('archive-no-results');
let currentYearFilter = '';
let currentKeywordFilters = new Set();

if (keywordFiltersContainer) {
  const btnsArray = Array.from(keywordBtns);
  btnsArray.sort((a, b) => parseInt(b.dataset.count) - parseInt(a.dataset.count));
  btnsArray.forEach(btn => keywordFiltersContainer.appendChild(btn));
}

let searchDebounceTimer;
searchInput.addEventListener('input', function(e) {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    filterItems(e.target.value.toLowerCase(), currentYearFilter, currentKeywordFilters);
  }, 100);
});

function updateURL() {
  const params = new URLSearchParams();
  if (currentYearFilter) params.set('year', currentYearFilter);
  if (currentKeywordFilters.size > 0) params.set('keyword', Array.from(currentKeywordFilters).join(','));
  const search = params.toString();
  history.replaceState(null, '', search ? '?' + search : location.pathname);
}

const archiveFiltersContainer = document.querySelector('.archive-filters');
if (archiveFiltersContainer) {
  archiveFiltersContainer.addEventListener('click', function(e) {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    filterBtns.forEach(b => b.classList.remove('filter-btn-active'));
    btn.classList.add('filter-btn-active');
    currentYearFilter = btn.dataset.year;
    filterItems(searchInput.value.toLowerCase(), currentYearFilter, currentKeywordFilters);
    updateURL();
  });
}

if (keywordFiltersContainer) {
  keywordFiltersContainer.addEventListener('click', function(e) {
    const btn = e.target.closest('.keyword-btn');
    if (!btn) return;
    btn.classList.toggle('keyword-btn-active');
    const keyword = btn.dataset.keyword;
    if (btn.classList.contains('keyword-btn-active')) {
      currentKeywordFilters.add(keyword);
    } else {
      currentKeywordFilters.delete(keyword);
    }
    filterItems(searchInput.value.toLowerCase(), currentYearFilter, currentKeywordFilters);
    updateURL();
  });
}

function matchesFilters(item, query, yearFilter, keywordFilters) {
  const title = item.dataset.title;
  const category = item.dataset.category;
  const excerpt = item.dataset.excerpt;
  const keywords = item.dataset.keywords ? item.dataset.keywords.split(',') : [];
  const searchMatch = title.includes(query) || category.includes(query) || excerpt.includes(query) || keywords.join(' ').includes(query);
  const yearMatch = yearFilter === '' || item.dataset.year === yearFilter;
  let keywordMatch = keywordFilters.size === 0;
  if (keywordFilters.size > 0) {
    keywordMatch = Array.from(keywordFilters).every(filter =>
      keywords.some(kw => kw.trim() === filter)
    );
  }
  return searchMatch && yearMatch && keywordMatch;
}

function filterItems(query, yearFilter, keywordFilters) {
  items.forEach(item => {
    item.style.display = matchesFilters(item, query, yearFilter, keywordFilters) ? 'block' : 'none';
  });
  yearHeadings.forEach(heading => {
    const year = heading.textContent.trim();
    const hasVisible = Array.from(items).some(item => item.dataset.year === year && item.style.display !== 'none');
    heading.style.display = hasVisible ? 'block' : 'none';
  });
  filterBtns.forEach(btn => {
    const btnYear = btn.dataset.year;
    const count = Array.from(items).filter(item => matchesFilters(item, query, btnYear, keywordFilters)).length;
    const countSpan = btn.querySelector('.count');
    if (countSpan) countSpan.textContent = `(${count})`;
  });
  keywordBtns.forEach(btn => {
    const expandedFilters = new Set(keywordFilters);
    expandedFilters.add(btn.dataset.keyword);
    const count = Array.from(items).filter(item => matchesFilters(item, query, yearFilter, expandedFilters)).length;
    const countSpan = btn.querySelector('.count');
    if (countSpan) countSpan.textContent = `(${count})`;
  });
  const visibleItems = Array.from(items).filter(item => item.style.display !== 'none').length;
  if (noResultsMessage) noResultsMessage.hidden = visibleItems !== 0;
}

const urlParams = new URLSearchParams(location.search);
const urlYear = urlParams.get('year') || '';
const urlKeywords = urlParams.get('keyword') ? urlParams.get('keyword').split(',') : [];
if (urlYear) {
  currentYearFilter = urlYear;
  filterBtns.forEach(btn => btn.classList.toggle('filter-btn-active', btn.dataset.year === urlYear));
}
urlKeywords.forEach(kw => {
  const trimmed = kw.trim();
  if (trimmed) {
    currentKeywordFilters.add(trimmed);
    keywordBtns.forEach(btn => { if (btn.dataset.keyword === trimmed) btn.classList.add('keyword-btn-active'); });
  }
});
filterItems(searchInput.value.toLowerCase(), currentYearFilter, currentKeywordFilters);
