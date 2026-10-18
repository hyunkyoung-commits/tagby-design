const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' })

  const token = (req.headers.authorization || '').replace('Bearer ', '')
  if (!token) return res.status(401).json({ error: '로그인이 필요합니다' })

  const { data: userData, error: authError } = await supabase.auth.getUser(token)
  if (authError || !userData?.user) return res.status(401).json({ error: '인증이 만료됐습니다' })

  const { data, error } = await supabase
    .from('articles')
    .select('slug, title, subtitle, category, cover_url, status, published_at, article_type, tags')
    .eq('author_id', userData.user.id)
    .order('published_at', { ascending: false })

  if (error) return res.status(500).json({ error: '조회 실패' })

  return res.status(200).json(data || [])
}
