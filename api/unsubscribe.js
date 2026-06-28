const { createClient } = require('@supabase/supabase-js')

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' })

  const { id } = req.query

  if (!id) {
    return res.status(400).send(errorPage('잘못된 수신 거부 링크입니다.'))
  }

  try {
    const { data: subscriber, error } = await supabase
      .from('subscribers')
      .select('id, email, status')
      .eq('id', id)
      .single()

    if (error || !subscriber) {
      return res.status(404).send(errorPage('구독 정보를 찾을 수 없습니다.'))
    }

    if (subscriber.status === 'unsubscribed') {
      return res.status(200).send(successPage('이미 수신 거부 처리된 이메일입니다.', subscriber.email))
    }

    await supabase
      .from('subscribers')
      .update({
        status: 'unsubscribed',
        unsubscribed_at: new Date().toISOString()
      })
      .eq('id', id)

    return res.status(200).send(successPage('수신 거부가 완료되었습니다.', subscriber.email))
  } catch (err) {
    console.error('unsubscribe error:', err)
    return res.status(500).send(errorPage('처리 중 오류가 발생했습니다.'))
  }
}

function successPage(message, email) {
  return `<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>수신 거부 완료 | TAGby</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
  <style>body{font-family:'Pretendard',sans-serif;background:#1A1A1A;color:#fff;min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0;}</style>
</head>
<body>
  <div style="text-align:center;padding:40px 24px;max-width:480px;">
    <div style="font-size:20px;font-weight:900;letter-spacing:3px;margin-bottom:48px;">TAGby</div>
    <div style="font-size:40px;margin-bottom:24px;">✓</div>
    <h1 style="font-size:20px;font-weight:700;margin:0 0 16px;">${message}</h1>
    <p style="font-size:14px;color:#888;line-height:1.7;margin:0 0 8px;">${email}</p>
    <p style="font-size:14px;color:#666;line-height:1.7;margin:0 0 40px;">더 이상 TAGby 뉴스레터가 발송되지 않습니다.</p>
    <a href="https://mkt.tagby.io" style="font-size:13px;color:#888;text-decoration:underline;">TAGby 홈으로 돌아가기</a>
  </div>
</body>
</html>`
}

function errorPage(message) {
  return `<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>오류 | TAGby</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
  <style>body{font-family:'Pretendard',sans-serif;background:#1A1A1A;color:#fff;min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0;}</style>
</head>
<body>
  <div style="text-align:center;padding:40px 24px;max-width:480px;">
    <div style="font-size:20px;font-weight:900;letter-spacing:3px;margin-bottom:48px;">TAGby</div>
    <h1 style="font-size:20px;font-weight:700;margin:0 0 16px;">${message}</h1>
    <a href="https://mkt.tagby.io" style="font-size:13px;color:#888;text-decoration:underline;">TAGby 홈으로 돌아가기</a>
  </div>
</body>
</html>`
}
