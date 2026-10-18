-- TAGby 아티클 CMS — Supabase 초기 설정
-- Supabase 대시보드 > SQL Editor에서 실행하세요

-- ── articles 테이블 ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  slug            TEXT UNIQUE NOT NULL,
  title           TEXT NOT NULL,
  subtitle        TEXT,
  body_html       TEXT,
  category        TEXT NOT NULL,
  tags            TEXT[] DEFAULT '{}',
  cover_url       TEXT,
  article_type    TEXT NOT NULL DEFAULT 'text',  -- 'text' | 'card-news'
  author_id       UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  author_email    TEXT,
  author_name     TEXT,
  status          TEXT NOT NULL DEFAULT 'published',  -- 'draft' | 'published'
  published_at    TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── article_slides 테이블 (카드뉴스 슬라이드) ─────────────────
CREATE TABLE IF NOT EXISTS article_slides (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  article_id  UUID REFERENCES articles(id) ON DELETE CASCADE NOT NULL,
  image_url   TEXT NOT NULL,
  sort_order  INTEGER NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── 인덱스 ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_articles_slug        ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_articles_status      ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_category    ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_published   ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_slides_article_id    ON article_slides(article_id);

-- ── updated_at 자동 갱신 트리거 ───────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_articles_updated_at ON articles;
CREATE TRIGGER set_articles_updated_at
  BEFORE UPDATE ON articles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── Row Level Security ────────────────────────────────────────
ALTER TABLE articles      ENABLE ROW LEVEL SECURITY;
ALTER TABLE article_slides ENABLE ROW LEVEL SECURITY;

-- 누구나 published 아티클 조회 가능
CREATE POLICY "Public read published articles"
  ON articles FOR SELECT
  USING (status = 'published');

-- 로그인한 사용자만 아티클 작성 가능
CREATE POLICY "Auth users insert articles"
  ON articles FOR INSERT
  TO authenticated
  WITH CHECK (author_id = auth.uid());

-- 본인 아티클만 수정 가능
CREATE POLICY "Auth users update own articles"
  ON articles FOR UPDATE
  TO authenticated
  USING (author_id = auth.uid());

-- published 아티클의 슬라이드 조회 가능
CREATE POLICY "Public read slides of published articles"
  ON article_slides FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM articles
      WHERE id = article_slides.article_id AND status = 'published'
    )
  );

-- 본인 아티클 슬라이드 관리
CREATE POLICY "Auth users manage own slides"
  ON article_slides FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM articles
      WHERE id = article_slides.article_id AND author_id = auth.uid()
    )
  );

-- ── Storage 버킷 생성 ─────────────────────────────────────────
-- Supabase 대시보드 > Storage에서 직접 생성하거나 아래 실행
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'article-images',
  'article-images',
  true,
  2097152,  -- 2MB (bytes)
  ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp']
)
ON CONFLICT (id) DO UPDATE SET
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- Storage: 로그인 사용자만 업로드 가능, 누구나 조회 가능
CREATE POLICY "Public read article images"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'article-images');

CREATE POLICY "Auth users upload article images"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = 'article-images');

CREATE POLICY "Auth users delete own article images"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id = 'article-images' AND auth.uid()::text = (storage.foldername(name))[1]);
