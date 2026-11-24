-- InkLink — contato por WhatsApp no agendamento
-- Guarda QUANDO o cliente usou o botão "Contatar tatuador no Whatsapp".
-- NULL = ainda não usou (botão disponível); preenchido = já usou (botão some, só 1 vez).
-- Rode no SQL Editor do Supabase. Pode rodar mais de uma vez.

ALTER TABLE agendamento ADD COLUMN IF NOT EXISTS whatsapp_enviado_em TIMESTAMPTZ;
