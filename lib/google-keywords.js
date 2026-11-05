// Server only. Never return OAuth credentials or raw provider errors to visitors.
const MONTHS = ['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER'];
const SEEDS = ['마케팅','디지털 마케팅','퍼포먼스 마케팅','콘텐츠 마케팅','인플루언서 마케팅','브랜딩','광고','검색 광고','SNS 마케팅','인스타그램 광고','유튜브 광고','네이버 광고','구글 광고','메타 광고','SEO','CRM','이메일 마케팅','숏폼','생성형 AI','마케팅 자동화','리타겟팅','전환율','브랜드 마케팅','바이럴 마케팅'];
const REQUIRED = ['GOOGLE_ADS_CLIENT_ID','GOOGLE_ADS_CLIENT_SECRET','GOOGLE_ADS_REFRESH_TOKEN','GOOGLE_ADS_CUSTOMER_ID'];
let cached, pending;
function volume(value) {
  if (value === null || value === undefined || value === '' || !/^[0-9]+$/.test(String(value))) return null;
  const n = Number(value);
  return Number.isSafeInteger(n) && n >= 0 ? n : null;
}
function normalize(results, now = new Date()) {
  const currentMonth = now.getUTCFullYear() * 12 + now.getUTCMonth();
  const seen = new Set();
  const rows = (results || []).filter(r => {
    if (typeof r.text !== 'string' || !r.text.trim() || seen.has(r.text)) return false;
    seen.add(r.text); return true;
  }).map(r => ({ keyword: r.text, months: new Map((r.keywordMetrics?.monthlySearchVolumes || []).flatMap(m => {
    const month = MONTHS.indexOf(m.month), year = Number(m.year), count = volume(m.monthlySearches);
    return month >= 0 && Number.isInteger(year) && year > 2000 && count !== null && year * 12 + month < currentMonth
      ? [[year * 12 + month, count]] : [];
  })) }));
  const latest = Math.max(...rows.flatMap(r => [...r.months.keys()]));
  // Never silently fall back to an older month to pad the ranking.
  const ranked = rows.filter(r => r.months.has(latest)).sort((a,b) => b.months.get(latest)-a.months.get(latest) || a.keyword.localeCompare(b.keyword,'ko')).slice(0,10);
  if (ranked.length < 10) return { status: 'unavailable', items: [] };
  return { status: 'ready', source: 'Google Ads Keyword Planner', scope: '선정한 마케팅 키워드 · 대한민국 · 한국어 · Google 검색', month: `${Math.floor(latest/12)}-${String(latest%12+1).padStart(2,'0')}`, updatedAt: now.toISOString(), items: ranked.map((r,i) => {
    const count = r.months.get(latest), previous = r.months.get(latest-1);
    return { rank:i+1, keyword:r.keyword, monthlySearches:count, previousMonthlySearches:previous ?? null, changePercent: previous > 0 ? Math.round((count-previous)/previous*1000)/10 : null };
  }) };
}
async function request(url, options) {
  const response = await fetch(url, {...options, signal: AbortSignal.timeout(7000)});
  if (!response.ok) throw new Error('Provider unavailable');
  return response.json();
}
async function load() {
  const token = await request('https://oauth2.googleapis.com/token', { method:'POST', body: new URLSearchParams({client_id:process.env.GOOGLE_ADS_CLIENT_ID, client_secret:process.env.GOOGLE_ADS_CLIENT_SECRET, refresh_token:process.env.GOOGLE_ADS_REFRESH_TOKEN, grant_type:'refresh_token'}) });
  if (!token.access_token) throw new Error('Provider unavailable');
  const customer = process.env.GOOGLE_ADS_CUSTOMER_ID.replace(/-/g,'');
  const version = process.env.GOOGLE_ADS_API_VERSION || 'v25';
  if (!/^\d+$/.test(customer) || !/^v\d+$/.test(version)) throw new Error('Invalid configuration');
  const headers = {Authorization:`Bearer ${token.access_token}`, 'Content-Type':'application/json'};
  if (process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID) headers['login-customer-id'] = process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID.replace(/-/g,'');
  const result = await request(`https://googleads.googleapis.com/${version}/customers/${customer}:generateKeywordHistoricalMetrics`, {method:'POST', headers, body:JSON.stringify({keywords:SEEDS, language:'languageConstants/1012', geoTargetConstants:['geoTargetConstants/2410'], keywordPlanNetwork:'GOOGLE_SEARCH'})});
  return normalize(result.results);
}
async function handler(req,res) {
  if (req.method !== 'GET') { res.setHeader('Allow','GET'); return res.status(405).json({error:'Method not allowed'}); }
  if (REQUIRED.some(name => !process.env[name])) { res.setHeader('Cache-Control','no-store'); return res.status(200).json({status:'not_configured',items:[]}); }
  try {
    if (!cached || Date.now() - cached.at > 86400000) {
      if (!pending) pending = load().then(data => { if(data.status === 'ready') cached={data,at:Date.now()}; return data; }).finally(() => {pending=null;});
      const data = await pending;
      if (data.status !== 'ready') {res.setHeader('Cache-Control','no-store');return res.status(200).json(data);}
    }
    res.setHeader('Cache-Control','public, s-maxage=3600, stale-while-revalidate=60');
    return res.status(200).json(cached.data);
  } catch { res.setHeader('Cache-Control','no-store'); return res.status(200).json({status:'unavailable',items:[]}); }
}
module.exports = { handler, normalize };
