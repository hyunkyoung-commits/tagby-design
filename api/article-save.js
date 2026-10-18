const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

const VALID_CATEGORIES = ['퍼포먼스마케팅', '콘텐츠마케팅', '디자인', 'AI']

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
  if (authError || !userData?.user) {
    return res.status(401).json({ error: '인증이 만료되었습니다. 다시 로그인해주세요.' })
  }

  const {
    slug,
    title,
    subtitle,
    body_html,
    category,
    tags,
    cover_url,
    article_type,
    slides,
    status,
    author_name,
    source_name,
    source_url
  } = req.body || {}

  // 필수값 검증
  if (!slug || !title || !category) {
    return res.status(400).json({ error: '슬러그, 제목, 카테고리는 필수입니다' })
  }
  if (!VALID_CATEGORIES.includes(category)) {
    return res.status(400).json({ error: '올바른 카테고리를 선택해주세요' })
  }
  if (article_type === 'card-news' && (!Array.isArray(slides) || slides.length === 0)) {
    return res.status(400).json({ error: '카드뉴스는 슬라이드 이미지가 최소 1장 필요합니다' })
  }
  if (article_type !== 'card-news' && !body_html) {
    return res.status(400).json({ error: '본문 내용을 입력해주세요' })
  }

  // 슬러그 형식 검증 (영문 소문자, 숫자, 하이픈만)
  if (!/^[a-z0-9-]+$/.test(slug)) {
    return res.status(400).json({ error: '슬러그는 영문 소문자, 숫자, 하이픈(-)만 사용 가능합니다' })
  }

  // 슬러그 중복 확인
  const { data: existing } = await supabase
    .from('articles')
    .select('id, author_id')
    .eq('slug', slug)
    .maybeSingle()

  if (existing && existing.author_id !== userData.user.id) {
    return res.status(409).json({ error: '이미 사용 중인 슬러그입니다. 다른 슬러그를 사용해주세요.' })
  }

  const articleData = {
    slug,
    title,
    subtitle: subtitle || null,
    body_html: body_html || null,
    category,
    tags: Array.isArray(tags) ? tags : [],
    cover_url: cover_url || null,
    article_type: article_type || 'text',
    author_id: userData.user.id,
    author_email: userData.user.email,
    author_name: author_name || userData.user.user_metadata?.name || userData.user.email.split('@')[0],
    status: status || 'published',
    published_at: new Date().toISOString(),
    source_name: source_name || null,
    source_url:  source_url  || null
  }

  // 같은 저자의 글이 이미 있으면 UPDATE, 아니면 INSERT
  let article, insertError
  if (existing) {
    const { data, error } = await supabase
      .from('articles')
      .update(articleData)
      .eq('id', existing.id)
      .select()
      .single()
    article = data; insertError = error
  } else {
    const { data, error } = await supabase
      .from('articles')
      .insert(articleData)
      .select()
      .single()
    article = data; insertError = error
  }

  if (insertError) {
    return res.status(500).json({ error: '저장에 실패했습니다: ' + insertError.message })
  }

  // 카드뉴스 슬라이드 저장
  if (article_type === 'card-news' && Array.isArray(slides) && slides.length > 0) {
    const slideRows = slides.map((slide, i) => ({
      article_id: article.id,
      image_url: typeof slide === 'string' ? slide : slide.url,
      caption: typeof slide === 'string' ? null : (slide.caption || null),
      sort_order: i
    }))

    const { error: slideError } = await supabase.from('article_slides').insert(slideRows)
    if (slideError) {
      // 아티클은 저장됐으나 슬라이드 실패 — 아티클 삭제 후 오류 반환
      await supabase.from('articles').delete().eq('id', article.id)
      return res.status(500).json({ error: '슬라이드 저장에 실패했습니다: ' + slideError.message })
    }
  }

  return res.status(200).json({ success: true, slug: article.slug, id: article.id })
}
