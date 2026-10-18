const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  if (req.method === 'OPTIONS') return res.status(200).end()

  const token = (req.headers.authorization || '').replace('Bearer ', '')
  if (!token) return res.status(401).json({ error: '로그인이 필요합니다' })

  const { data: userData, error: authError } = await supabase.auth.getUser(token)
  if (authError || !userData?.user) return res.status(401).json({ error: '인증이 만료됐습니다' })

  const userId = userData.user.id

  // GET → 내 아티클 목록
  if (req.method === 'GET') {
    const { data, error } = await supabase
      .from('articles')
      .select('slug, title, subtitle, category, cover_url, status, published_at, article_type, tags')
      .eq('author_id', userId)
      .order('published_at', { ascending: false })
    if (error) return res.status(500).json({ error: '조회 실패' })
    return res.status(200).json(data || [])
  }

  if (req.method === 'POST') {
    const { action, slug } = req.body || {}
    if (!action || !slug) return res.status(400).json({ error: '잘못된 요청' })

    // POST { action: 'get', slug } → 단일 아티클 (수정용, draft 포함)
    if (action === 'get') {
      const { data, error } = await supabase
        .from('articles')
        .select('*')
        .eq('slug', slug)
        .eq('author_id', userId)
        .maybeSingle()
      if (error || !data) return res.status(404).json({ error: '아티클을 찾을 수 없습니다' })
      return res.status(200).json(data)
    }

    // POST { action: 'delete', slug } → 삭제
    if (action === 'delete') {
      const { error } = await supabase
        .from('articles')
        .delete()
        .eq('slug', slug)
        .eq('author_id', userId)
      if (error) return res.status(500).json({ error: '삭제 실패' })
      return res.status(200).json({ success: true })
    }

    return res.status(400).json({ error: '알 수 없는 action' })
  }

  return res.status(405).json({ error: 'Method not allowed' })
}
