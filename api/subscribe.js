const { createClient } = require('@supabase/supabase-js')
const nodemailer = require('nodemailer')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

function createTransporter() {
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
      user: process.env.GMAIL_USER,
      pass: process.env.GMAIL_APP_PASSWORD
    }
  })
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const { email, name } = req.body || {}

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: '올바른 이메일을 입력해주세요.' })
  }

  const normalizedEmail = email.toLowerCase().trim()

  try {
    const { data: existing } = await supabase
      .from('subscribers')
      .select('id, status')
      .eq('email', normalizedEmail)
      .single()

    if (existing?.status === 'active') {
      return res.status(409).json({ error: '이미 구독 중인 이메일입니다.' })
    }

    let subscriberId

    if (existing?.status === 'unsubscribed') {
      const { data } = await supabase
        .from('subscribers')
        .update({
          status: 'active',
          name: name?.trim() || existing.name,
          subscribed_at: new Date().toISOString(),
          unsubscribed_at: null
        })
        .eq('email', normalizedEmail)
        .select('id')
        .single()
      subscriberId = data?.id
    } else {
      const { data, error } = await supabase
        .from('subscribers')
        .insert({ email: normalizedEmail, name: name?.trim() || null })
        .select('id')
        .single()

      if (error) throw error
      subscriberId = data?.id
    }

    // 환영 이메일 발송
    const transporter = createTransporter()
    await transporter.sendMail({
      from: `TAGby 뉴스레터 <${process.env.GMAIL_USER}>`,
      to: normalizedEmail,
      subject: 'TAGby 뉴스레터 구독을 환영합니다',
      html: welcomeEmailHtml({ name: name?.trim(), email: normalizedEmail, id: subscriberId })
    })

    return res.status(200).json({ success: true, message: '구독 완료! 환영 이메일을 보내드렸습니다.' })
  } catch (err) {
    console.error('subscribe error:', err)
    return res.status(500).json({ error: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' })
  }
}

function welcomeEmailHtml({ name, email, id }) {
  const unsubscribeUrl = `https://mkt.tagby.io/api/unsubscribe?id=${id}`
  const greeting = name ? `${name}님, 환영합니다!` : '구독해 주셔서 감사합니다!'

  return `<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TAGby 뉴스레터 환영합니다</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background:#1A1A1A;padding:36px 40px;text-align:center;">
            <div style="font-size:22px;font-weight:900;color:#ffffff;letter-spacing:3px;">TAGby</div>
            <div style="font-size:12px;color:#888888;margin-top:6px;letter-spacing:1px;">MARKETING INSIGHTS</div>
          </td>
        </tr>
        <tr>
          <td style="padding:48px 40px 40px;">
            <h1 style="margin:0 0 20px;font-size:22px;font-weight:800;color:#1A1A1A;">${greeting}</h1>
            <p style="margin:0 0 16px;font-size:15px;color:#555555;line-height:1.8;">TAGby 뉴스레터를 구독해 주셨습니다.</p>
            <p style="margin:0 0 16px;font-size:15px;color:#555555;line-height:1.8;">퍼포먼스 마케팅, 콘텐츠 마케팅, 디자인 트렌드까지 —<br>실무에 바로 쓸 수 있는 인사이트를 정기적으로 보내드릴게요.</p>
            <div style="margin-top:36px;">
              <a href="https://mkt.tagby.io/tagby-article.html" style="display:inline-block;background:#1A1A1A;color:#ffffff;text-decoration:none;padding:14px 32px;border-radius:8px;font-size:14px;font-weight:600;letter-spacing:0.5px;">아티클 둘러보기 →</a>
            </div>
          </td>
        </tr>
        <tr>
          <td style="padding:0 40px;"><div style="height:1px;background:#eeeeee;"></div></td>
        </tr>
        <tr>
          <td style="padding:28px 40px;background:#fafafa;">
            <p style="margin:0;font-size:12px;color:#aaaaaa;line-height:1.7;">
              TAGby | 서울특별시 강남구 테헤란로 418 다봉빌딩 11층<br>
              이 메일은 <strong>${email}</strong>로 발송되었습니다.
            </p>
            <p style="margin:12px 0 0;font-size:12px;">
              <a href="${unsubscribeUrl}" style="color:#aaaaaa;text-decoration:underline;">수신 거부하기</a>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`
}
