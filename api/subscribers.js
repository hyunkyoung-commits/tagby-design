const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const { password, action } = req.body || {}

  if (password !== process.env.ADMIN_PASSWORD) {
    return res.status(401).json({ error: '비밀번호가 틀렸습니다.' })
  }

  try {
    // 아티클 회원 목록 (Vercel Hobby 함수 12개 제한 때문에 별도 파일 대신 여기에 통합)
    if (action === 'members') {
      const users = []
      const perPage = 1000
      for (let page = 1; page <= 20; page++) {
        const { data, error } = await supabase.auth.admin.listUsers({ page, perPage })
        if (error) throw error
        users.push(...data.users)
        if (data.users.length < perPage) break
      }

      const { data: articles, error: articleError } = await supabase
        .from('articles')
        .select('author_id')
      if (articleError) throw articleError

      const articleCounts = {}
      for (const a of articles || []) {
        if (a.author_id) articleCounts[a.author_id] = (articleCounts[a.author_id] || 0) + 1
      }

      const members = users
        .map(u => ({
          id: u.id,
          email: u.email,
          name: u.user_metadata?.name || (u.email ? u.email.split('@')[0] : ''),
          created_at: u.created_at,
          last_sign_in_at: u.last_sign_in_at || null,
          article_count: articleCounts[u.id] || 0
        }))
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

      return res.status(200).json({ members })
    }

    if (action === 'list') {
      const { data, error } = await supabase
        .from('subscribers')
        .select('id, name, email, status, subscribed_at')
        .order('subscribed_at', { ascending: false })
        .limit(500)

      if (error) throw error
      return res.status(200).json({ subscribers: data || [] })
    }

    const { count: activeCount } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'active')

    const { count: totalCount } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })

    const { data: recentLogs } = await supabase
      .from('newsletter_logs')
      .select('id, subject, issue_number, recipient_count, articles, sent_at')
      .order('sent_at', { ascending: false })
      .limit(50)

    return res.status(200).json({
      active: activeCount || 0,
      total: totalCount || 0,
      recentLogs: recentLogs || []
    })
  } catch (err) {
    console.error('subscribers error:', err)
    return res.status(500).json({ error: '서버 오류가 발생했습니다.' })
  }
}
