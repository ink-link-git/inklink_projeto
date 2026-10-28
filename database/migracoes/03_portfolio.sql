-- InkLink — portfólio
-- Módulo portfolio_tatuador.
-- Rode no SQL Editor do Supabase. Pode rodar mais de uma vez (usa IF NOT EXISTS).
-- As tabelas 'cliente', 'tatuador' e 'portfolio' já existem e não são alteradas aqui.

-- 4. PORTFÓLIO (a tabela já existe; só garante o que o código usa) ---------
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS data_upload TIMESTAMP DEFAULT NOW();

-- Bucket das imagens do portfólio (público)
INSERT INTO storage.buckets (id, name, public) VALUES ('portfolio_images', 'portfolio_images', TRUE) ON CONFLICT (id) DO NOTHING;
