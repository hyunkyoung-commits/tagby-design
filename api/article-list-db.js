const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' })

  const { category, limit = 50 } = req.query

  let query = supabase
    .from('articles')
    .select('slug, title, subtitle, published_at, category, cover_url, tags, article_type, author_name')
    .eq('status', 'published')
    .order('published_at', { ascending: false })
    .limit(Math.min(parseInt(limit) || 50, 200))

  if (category) query = query.eq('category', category)

  const { data, error } = await query

  if (error) return res.status(500).json({ error: '목록 조회에 실패했습니다' })

  // articles.json 형식과 호환되는 구조로 반환
  const articles = (data || []).map(a => ({
    slug: a.slug,
    title: a.title,
    subtitle: a.subtitle || '',
    date: a.published_at ? a.published_at.slice(0, 10) : '',
    category: a.category,
    cover: a.cover_url || null,
    tags: a.tags || [],
    article_type: a.article_type || 'text',
    author_name: a.author_name || '',
    source: 'db'
  }))

  return res.status(200).json(articles)
}
