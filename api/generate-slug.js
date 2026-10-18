module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const { title } = req.body || {}
  if (!title) return res.status(400).json({ error: 'title is required' })

  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) return res.status(500).json({ error: 'API key not configured' })

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 20,
        messages: [{
          role: 'user',
          content: `Convert this article title to a short English URL slug (3-5 words, lowercase, hyphens only, no date, capture key meaning): "${title}"\nRespond with ONLY the slug, nothing else.`
        }]
      })
    })

    const data = await response.json()
    const raw = (data.content?.[0]?.text || '').trim()
    const slug = raw
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 50)

    if (!slug) return res.status(500).json({ error: 'empty slug generated' })
    return res.status(200).json({ slug })
  } catch (e) {
    return res.status(500).json({ error: e.message })
  }
}
