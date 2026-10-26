const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

// 작성자 본인이 아니어도 모든 아티클을 조회/삭제할 수 있는 관리자 계정
const ADMIN_EMAILS = ['hyunkyoung@tagby.io']

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
  const isAdmin = ADMIN_EMAILS.includes(userData.user.email)

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
    if (!action) return res.status(400).json({ error: '잘못된 요청' })

    // POST { action: 'admin-list-users' } → 관리자 전용, 팀원 계정 목록 (작성자 변경 대상 찾기용)
    if (action === 'admin-list-users') {
      if (!isAdmin) return res.status(403).json({ error: '관리자만 사용할 수 있습니다' })
      const { data, error } = await supabase.auth.admin.listUsers()
      if (error) return res.status(500).json({ error: '사용자 목록 조회 실패' })
      const users = (data.users || []).map(u => ({
        id: u.id,
        email: u.email,
        name: u.user_metadata?.name || (u.email ? u.email.split('@')[0] : '')
      }))
      return res.status(200).json(users)
    }

    // POST { action: 'admin-set-author', slug, newAuthorEmail } → 관리자 전용, 아티클 작성자를 다른 계정으로 변경
    if (action === 'admin-set-author') {
      if (!isAdmin) return res.status(403).json({ error: '관리자만 사용할 수 있습니다' })
      const { newAuthorEmail } = req.body || {}
      if (!slug || !newAuthorEmail) return res.status(400).json({ error: 'slug와 newAuthorEmail이 필요합니다' })

      const { data: userList, error: listErr } = await supabase.auth.admin.listUsers()
      if (listErr) return res.status(500).json({ error: '사용자 조회 실패' })
      const target = (userList.users || []).find(u => u.email === newAuthorEmail)
      if (!target) return res.status(404).json({ error: '해당 이메일의 계정을 찾을 수 없습니다: ' + newAuthorEmail })

      const newName = target.user_metadata?.name || target.email.split('@')[0]
      const { error } = await supabase
        .from('articles')
        .update({ author_id: target.id, author_email: target.email, author_name: newName })
        .eq('slug', slug)
      if (error) return res.status(500).json({ error: '작성자 변경 실패' })

      return res.status(200).json({ success: true, author_id: target.id, author_email: target.email, author_name: newName })
    }

    if (!slug) return res.status(400).json({ error: '잘못된 요청' })

    // POST { action: 'get', slug } → 단일 아티클 (수정용, draft 포함)
    // 관리자는 작성자 본인이 아니어도 조회 가능
    if (action === 'get') {
      let query = supabase.from('articles').select('*').eq('slug', slug)
      if (!isAdmin) query = query.eq('author_id', userId)
      const { data, error } = await query.maybeSingle()
      if (error || !data) return res.status(404).json({ error: '아티클을 찾을 수 없습니다' })

      // 카드뉴스는 슬라이드도 함께 반환 (수정 화면에서 불러오기 위함)
      if (data.article_type === 'card-news') {
        const { data: slides } = await supabase
          .from('article_slides')
          .select('image_url, caption, sort_order')
          .eq('article_id', data.id)
          .order('sort_order', { ascending: true })
        data.slides = (slides || []).map(s => ({ url: s.image_url, caption: s.caption || '' }))
      }

      return res.status(200).json(data)
    }

    // POST { action: 'delete', slug } → 삭제 (관리자는 작성자 무관하게 삭제 가능)
    if (action === 'delete') {
      let query = supabase.from('articles').delete().eq('slug', slug)
      if (!isAdmin) query = query.eq('author_id', userId)
      const { error } = await query
      if (error) return res.status(500).json({ error: '삭제 실패' })
      return res.status(200).json({ success: true })
    }

    return res.status(400).json({ error: '알 수 없는 action' })
  }

  return res.status(405).json({ error: 'Method not allowed' })
}
