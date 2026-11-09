-- InkLink — libera o servidor Flask para gravar nas tabelas novas.
-- Rode no SQL Editor do Supabase (pode rodar mais de uma vez).
--
-- Por que: o servidor usa a chave pública (anon). Com o RLS ligado e sem nenhuma regra,
-- o Supabase bloqueia toda gravação ("new row violates row-level security policy").
--
-- Esta é a opção SIMPLES (boa para desenvolvimento/TCC): desliga o RLS nas tabelas do sistema
-- e libera o envio/leitura de imagens nos dois buckets.
-- A opção MAIS SEGURA é manter o RLS ligado e colocar SUPABASE_SERVICE_KEY no .env (veja o README).

-- 1. Tabelas do sistema -----------------------------------------------------
ALTER TABLE agendamento       DISABLE ROW LEVEL SECURITY;
ALTER TABLE referencia_visual DISABLE ROW LEVEL SECURITY;
ALTER TABLE anamnese          DISABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio         DISABLE ROW LEVEL SECURITY;

-- 2. Imagens (Storage) -------------------------------------------------------
-- Sem estas regras o upload de portfólio e de referências falha com erro de RLS.
DROP POLICY IF EXISTS "inklink_imagens_leitura" ON storage.objects;
CREATE POLICY "inklink_imagens_leitura" ON storage.objects
    FOR SELECT TO public
    USING (bucket_id IN ('portfolio_images', 'referencias'));

DROP POLICY IF EXISTS "inklink_imagens_envio" ON storage.objects;
CREATE POLICY "inklink_imagens_envio" ON storage.objects
    FOR INSERT TO public
    WITH CHECK (bucket_id IN ('portfolio_images', 'referencias'));

DROP POLICY IF EXISTS "inklink_imagens_atualiza" ON storage.objects;
CREATE POLICY "inklink_imagens_atualiza" ON storage.objects
    FOR UPDATE TO public
    USING (bucket_id IN ('portfolio_images', 'referencias'));
