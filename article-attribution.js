/* 아티클 유입 추적(최초 유입 기준): 아티클 페이지 첫 방문 시 slug와 시각을 localStorage에 기록하고,
   contact.html 제출 시 window.getArticleAttribution()으로 읽어 함께 전송한다. */
(function () {
  var KEY = 'tagby_article_attr';
  var WINDOW_DAYS = 30;
  var MAX_HISTORY = 10;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || { history: [] }; }
    catch (e) { return { history: [] }; }
  }
  function save(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }
  function fresh(list) {
    var cutoff = Date.now() - WINDOW_DAYS * 86400000;
    return (list || []).filter(function (x) { return x.ts >= cutoff; });
  }

  function currentSlug() {
    var p = location.pathname;
    if (/\/article-view(\.html)?$/.test(p)) {
      return new URLSearchParams(location.search).get('slug') || '';
    }
    var m = p.match(/\/design-study-article\/([^\/]+?)(?:\.html)?\/?$/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  var slug = currentSlug();
  if (slug) {
    var d = load();
    var h = fresh(d.history);
    var seen = h.some(function (x) { return x.slug === slug; });
    if (!seen && h.length < MAX_HISTORY) h.push({ slug: slug, ts: Date.now() });
    d.history = h;
    save(d);
  }

  // 문의 제출 시 호출: 30일 안에 처음 본 아티클을 반환, 없으면 빈 값
  window.getArticleAttribution = function () {
    var h = fresh(load().history);
    if (!h.length) return { article: '', visitedAt: '', history: '' };
    return {
      article: h[0].slug,
      visitedAt: new Date(h[0].ts).toISOString(),
      history: h.map(function (x) { return x.slug; }).join(',')
    };
  };
})();
