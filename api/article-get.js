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

  const { slug } = req.query
  if (!slug) return res.status(400).json({ error: 'slug가 필요합니다' })

  const { data: article, error } = await supabase
    .from('articles')
    .select('*')
    .eq('slug', slug)
    .eq('status', 'published')
    .single()

  if (error || !article) {
    return res.status(404).json({ error: '아티클을 찾을 수 없습니다' })
  }

  // 카드뉴스인 경우 슬라이드 조회
  if (article.article_type === 'card-news') {
    const { data: slides } = await supabase
      .from('article_slides')
      .select('image_url, caption, sort_order')
      .eq('article_id', article.id)
      .order('sort_order', { ascending: true })

    article.slides = (slides || []).map(s => ({ url: s.image_url, caption: s.caption || null }))
  }

  return res.status(200).json(article)
}
