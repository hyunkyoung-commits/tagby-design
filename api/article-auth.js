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

  const { action, email, password } = req.body || {}

  if (action === 'login') {
    if (!email || !password) {
      return res.status(400).json({ error: '이메일과 비밀번호를 입력해주세요' })
    }

    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) return res.status(401).json({ error: '로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.' })

    return res.status(200).json({
      access_token: data.session.access_token,
      user: {
        id: data.user.id,
        email: data.user.email,
        name: data.user.user_metadata?.name || data.user.email.split('@')[0]
      }
    })
  }

  if (action === 'signup') {
    const { email, password, name } = req.body || {}
    if (!email || !password) return res.status(400).json({ error: '이메일과 비밀번호를 입력해주세요' })
    if (password.length < 8) return res.status(400).json({ error: '비밀번호는 8자 이상이어야 합니다' })

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { name: name || email.split('@')[0] } }
    })
    if (error) return res.status(400).json({ error: error.message })
    if (!data.session) return res.status(400).json({ error: '가입에 실패했습니다. 이미 사용 중인 이메일일 수 있습니다.' })

    return res.status(200).json({
      access_token: data.session.access_token,
      user: {
        id: data.user.id,
        email: data.user.email,
        name: name || data.user.email.split('@')[0]
      }
    })
  }

  if (action === 'verify') {
    const token = (req.headers.authorization || '').replace('Bearer ', '')
    if (!token) return res.status(401).json({ error: '토큰이 없습니다' })

    const { data, error } = await supabase.auth.getUser(token)
    if (error || !data?.user) return res.status(401).json({ error: '인증이 만료되었습니다' })

    return res.status(200).json({
      user: {
        id: data.user.id,
        email: data.user.email,
        name: data.user.user_metadata?.name || data.user.email.split('@')[0]
      }
    })
  }

  return res.status(400).json({ error: '잘못된 요청입니다' })
}
