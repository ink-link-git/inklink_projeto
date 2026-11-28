-- InkLink — foto de perfil do cliente
-- Guarda a URL pública da foto (bucket 'avatars' do Supabase Storage, o mesmo do tatuador).
-- NULL = cliente sem foto (a tela mostra as iniciais do nome).
-- Rode no SQL Editor do Supabase ANTES de subir o código novo. Pode rodar mais de uma vez.

ALTER TABLE cliente ADD COLUMN IF NOT EXISTS avatar_url TEXT;
