const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

const MAX_SIZE_BYTES = 2 * 1024 * 1024  // 2MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  // 인증 확인
  const token = (req.headers.authorization || '').replace('Bearer ', '')
  if (!token) return res.status(401).json({ error: '로그인이 필요합니다' })

  const { data: userData, error: authError } = await supabase.auth.getUser(token)
  if (authError || !userData?.user) return res.status(401).json({ error: '인증이 만료되었습니다. 다시 로그인해주세요.' })

  const { base64, filename, contentType, thumbFor } = req.body || {}
  if (!base64 || !filename) return res.status(400).json({ error: '이미지 데이터가 없습니다' })

  // MIME 타입 검증
  const mimeType = contentType || 'image/jpeg'
  if (!ALLOWED_TYPES.includes(mimeType)) {
    return res.status(400).json({ error: 'JPG, PNG, GIF, WebP 형식만 업로드 가능합니다' })
  }

  // 파일 크기 검증 (서버 사이드)
  const buffer = Buffer.from(base64, 'base64')
  if (buffer.length > MAX_SIZE_BYTES) {
    const sizeMB = (buffer.length / 1024 / 1024).toFixed(1)
    return res.status(400).json({
      error: `이미지는 2MB 이하로 업로드해주세요 (현재: ${sizeMB}MB)`
    })
  }

  // 파일명 생성: 타임스탬프 + 랜덤 문자열
  const ext = filename.split('.').pop().toLowerCase().replace(/[^a-z0-9]/g, '')
  const safeExt = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext) ? ext : 'jpg'
  let storageName = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${safeExt}`

  // 카드용 썸네일: 원본 파일명 + '-thumb.webp' 규칙 (tagby-article.html 이 같은 규칙으로 조회)
  let isThumb = false
  if (thumbFor) {
    const m = /^(\d+-[a-z0-9]{1,8})\.(jpg|jpeg|png|gif|webp)$/.exec(String(thumbFor))
    if (!m || mimeType !== 'image/webp') {
      return res.status(400).json({ error: '썸네일 요청이 올바르지 않습니다' })
    }
    storageName = `${m[1]}-thumb.webp`
    isThumb = true
  }

  const { error: uploadError } = await supabase.storage
    .from('article-images')
    .upload(storageName, buffer, {
      contentType: mimeType,
      upsert: isThumb
    })

  if (uploadError) {
    return res.status(500).json({ error: '이미지 업로드에 실패했습니다: ' + uploadError.message })
  }

  const { data: { publicUrl } } = supabase.storage
    .from('article-images')
    .getPublicUrl(storageName)

  return res.status(200).json({ url: publicUrl, filename: storageName })
}
