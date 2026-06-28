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

  const { password } = req.body || {}

  if (password !== process.env.ADMIN_PASSWORD) {
    return res.status(401).json({ error: '비밀번호가 틀렸습니다.' })
  }

  try {
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
