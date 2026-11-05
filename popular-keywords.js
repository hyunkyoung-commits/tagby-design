(() => {
  const root = document.getElementById('popular-keywords');
  if (!root) return;
  const link = root.querySelector('.popular-link');
  const controls = root.querySelector('.popular-controls');
  const toggle = root.querySelector('[data-pause]');
  let items = [], index = 0, timer, paused = matchMedia('(prefers-reduced-motion: reduce)').matches, hovering = false;
  function stop() { clearInterval(timer); }
  function start() {
    stop();
    toggle.textContent = paused ? '▶' : 'Ⅱ';
    toggle.setAttribute('aria-label', paused ? '검색어 자동 넘김 재생' : '검색어 자동 넘김 일시정지');
    toggle.setAttribute('aria-pressed', String(paused));
    if (items.length > 1 && !paused && !hovering && !root.contains(document.activeElement) && !document.hidden) timer = setInterval(() => show(index+1), 3800);
  }
  function show(next) {
    index = (next + items.length) % items.length;
    const item = items[index];
    root.querySelector('.popular-rank').textContent = `${item.rank}`;
    root.querySelector('.popular-word').textContent = item.keyword;
    root.querySelector('.popular-volume').textContent = `${item.monthlySearches.toLocaleString('ko-KR')}회`;
    const change = root.querySelector('.popular-change');
    const n = item.changePercent;
    change.className = 'popular-change ' + (n > 0 ? 'up' : n < 0 ? 'down' : 'flat');
    change.textContent = n === null ? '비교 불가' : n === 0 ? '— 0%' : `${n > 0 ? '▲' : '▼'} ${Math.abs(n)}%`;
    change.setAttribute('aria-label', n === null ? '전월 비교 불가' : `전월 대비 ${Math.abs(n)}% ${n > 0 ? '증가' : n < 0 ? '감소' : '변동 없음'}`);
    link.href = `tagby-article.html?q=${encodeURIComponent(item.keyword)}`;
  }
  link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    window.searchArticles(items[index].keyword);
    document.getElementById('article-query').focus({preventScroll:true});
    document.getElementById('article-search').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',block:'start'});
  });
  root.addEventListener('mouseenter', () => { hovering = true; stop(); });
  root.addEventListener('mouseleave', () => { hovering = false; start(); });
  root.addEventListener('focusin', stop);
  root.addEventListener('focusout', () => setTimeout(start,0));
  document.addEventListener('visibilitychange', start);
  toggle.addEventListener('click', () => {paused=!paused;start();});
  root.querySelector('[data-next]').addEventListener('click', () => {show(index+1);start();});
  fetch('/api/article-list-db?resource=popular-keywords', {signal:AbortSignal.timeout(20000)})
    .then(r => { if(!r.ok) throw new Error(); return r.json(); })
    .then(data => {
      if (data.status === 'unavailable') root.querySelector('[data-placeholder]').textContent = '검색량을 불러오지 못했습니다';
      if(data.status !== 'ready' || !Array.isArray(data.items) || data.items.length !== 10 || !data.items.every((x,i) => x.rank === i+1 && typeof x.keyword === 'string' && Number.isSafeInteger(x.monthlySearches) && x.monthlySearches >= 0 && (x.changePercent === null || Number.isFinite(x.changePercent)))) return;
      items = data.items;
      root.querySelector('[data-placeholder]').hidden = true;
      link.hidden = false; controls.hidden = false;
      root.querySelector('[data-source]').textContent = `${data.month} · Google Ads 월간 검색량(추정치). ${data.scope}. 최신 제공 월 기준 TOP 10이며 전체 검색어 순위가 아닙니다. 증감률은 직전 월 대비이며 이전 값이 없거나 0이면 비교 불가로 표시합니다.`;
      show(0); start();
    }).catch(() => {root.querySelector('[data-placeholder]').textContent='검색량을 불러오지 못했습니다';});
})();
