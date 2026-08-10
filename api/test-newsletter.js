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

  const { password, subject, intro, articles, issueNumber, testEmail } = req.body || {}

  if (password !== process.env.ADMIN_PASSWORD) {
    return res.status(401).json({ error: '비밀번호가 틀렸습니다.' })
  }

  if (!subject?.trim()) return res.status(400).json({ error: '제목을 입력해주세요.' })
  if (!articles?.length) return res.status(400).json({ error: '아티클을 1개 이상 추가해주세요.' })

  const to = testEmail || process.env.GMAIL_USER

  try {
    const transporter = createTransporter()
    await transporter.sendMail({
      from: `TAGby 뉴스레터 <${process.env.GMAIL_USER}>`,
      to,
      subject: `[테스트] ${subject}`,
      html: newsletterHtml({ subject, intro, articles, issueNumber, email: to })
    })

    return res.status(200).json({ success: true, sentTo: to })
  } catch (err) {
    console.error('test-newsletter error:', err)
    return res.status(500).json({ error: '발송 오류: ' + err.message })
  }
}

function newsletterHtml({ subject, intro, articles, issueNumber, email }) {
  const R2_PUBLIC_URL = 'https://pub-b1df54740a134d2d96bd71640abf62ce.r2.dev'

  const articleItems = articles.map((article, index) => `
    <tr>
      <td style="padding:0 0 32px;">
        <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #eeeeee;border-radius:10px;overflow:hidden;">
          ${article.imageUrl ? `<tr><td style="padding:0;"><a href="${article.imageUrl}" target="_blank" style="display:block;"><img src="${article.imageUrl}" alt="${escapeHtml(article.title)}" width="100%" style="display:block;width:100%;height:auto;"></a></td></tr>` : ''}
          <tr>
            <td style="padding:28px 32px;">
              <div style="font-size:11px;font-weight:700;color:#0078F0;letter-spacing:2px;margin-bottom:10px;">0${index + 1}</div>
              <h2 style="margin:0 0 10px;font-size:17px;font-weight:800;color:#1A1A1A;line-height:1.4;">${escapeHtml(article.title)}</h2>
              ${article.description ? `<p style="margin:0 0 20px;font-size:14px;color:#666666;line-height:1.7;">${escapeHtml(article.description)}</p>` : ''}
              <a href="${article.url}" style="display:inline-block;font-size:13px;font-weight:600;color:#0078F0;text-decoration:none;border-bottom:1px solid #0078F0;padding-bottom:2px;">계속 읽기 →</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>`).join('')

  return `<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(subject)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background:#1A1A1A;padding:36px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <div style="font-size:20px;font-weight:900;color:#ffffff;letter-spacing:3px;">TAGby</div>
                  <div style="font-size:11px;color:#888888;margin-top:5px;letter-spacing:1px;">MARKETING INSIGHTS</div>
                </td>
                ${issueNumber ? `<td align="right"><div style="font-size:11px;color:#666666;letter-spacing:1px;">ISSUE #${issueNumber}</div></td>` : ''}
              </tr>
            </table>
          </td>
        </tr>
        ${intro ? `<tr><td style="padding:48px 40px 36px;">
          <p style="margin:0;font-size:15px;color:#555555;line-height:1.8;">${escapeHtml(intro).replace(/\n/g, '<br>')}</p>
        </td></tr>` : `<tr><td style="padding:24px;"></td></tr>`}
        <tr>
          <td style="padding:0 40px;">
            <table width="100%" cellpadding="0" cellspacing="0">${articleItems}</table>
          </td>
        </tr>
        <tr>
          <td style="padding:8px 40px 48px;text-align:center;">
            <a href="https://mkt.tagby.io/tagby-article.html" style="display:inline-block;background:#1A1A1A;color:#ffffff;text-decoration:none;padding:14px 36px;border-radius:8px;font-size:14px;font-weight:600;letter-spacing:0.5px;">전체 아티클 보기</a>
          </td>
        </tr>
        <tr>
          <td style="padding:0 40px;"><div style="height:1px;background:#eeeeee;"></div></td>
        </tr>
        <tr>
          <td style="padding:28px 40px;background:#fafafa;">
            <p style="margin:0;font-size:12px;color:#aaaaaa;line-height:1.7;">
              TAGby | 서울특별시 강남구 테헤란로 418 다봉빌딩 11층<br>
              이 메일은 <strong>${email}</strong>로 발송되었습니다. <span style="color:#ff6b6b;">[테스트 발송]</span>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`
}

function escapeHtml(str) {
  if (!str) return ''
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}
