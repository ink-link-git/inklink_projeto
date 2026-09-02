
-- 1. TATUADOR

CREATE TABLE Tatuador (
    id_tatuador INT AUTO_INCREMENT PRIMARY KEY, -- Identificador único do tatuador
    nome VARCHAR(100) NOT NULL,                 -- Nome completo do profissional
    cpf VARCHAR(14) UNIQUE NOT NULL,            -- CPF para identificação e emissão de cobranças do SaaS
    email VARCHAR(100) UNIQUE NOT NULL,         -- E-mail para login no sistema web
    senha_hash VARCHAR(255) NOT NULL,           -- Hash seguro da senha de acesso (nunca texto puro)
    tel VARCHAR(20) NOT NULL,                   -- WhatsApp/Telefone de contato do tatuador
    especialidade VARCHAR(100),                 -- Estilo principal (ex: Blackwork, Fineline, Realismo)
   );


-- 2. CLIENTE

CREATE TABLE Cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,   -- Identificador único do cliente
    id_tatuador INT NOT NULL,                    -- FK: Garante a privacidade (cada tatuador só vê seus próprios clientes)
    nome VARCHAR(100) NOT NULL,                  -- Nome completo do cliente
    cpf VARCHAR(14),                             -- CPF do cliente (opcional para ficha)
    tel VARCHAR(20) NOT NULL,                    -- Telefone/WhatsApp principal para envio de lembretes
    email VARCHAR(100),                          -- E-mail de contato
    data_nascimento DATE,                        -- Utilizado para verificar se o cliente é maior de idade
    FOREIGN KEY (id_tatuador) REFERENCES Tatuador(id_tatuador) ON DELETE CASCADE
);


-- 3. IDEIAS E ORÇAMENTOS 

CREATE TABLE Ideia_Tatuagem (
    id_ideia INT AUTO_INCREMENT PRIMARY KEY,     -- Identificador único da ideia/projeto
    id_cliente INT NOT NULL,                     -- FK: Cliente que solicitou o orçamento
    descricao TEXT NOT NULL,                     -- Detalhamento da ideia do cliente (ex: "Leão no antebraço")
    local_corpo VARCHAR(50),                     -- Parte do corpo onde será feita (ex: Antebraço, Costas)
    tamanho_cm DECIMAL(5,2),                     -- Tamanho aproximado em centímetros (ex: 15.5)
    nivel_complexidade ENUM('BAIXA', 'MEDIA', 'ALTA') DEFAULT 'MEDIA', -- Utilizado na lógica de cálculo de preço
    valor_estimado DECIMAL(10,2),                -- Preço calculado com base no tamanho e complexidade
    status ENUM('EM_ANALISE', 'APROVADO', 'DESCARTADO') DEFAULT 'EM_ANALISE', -- Estado do orçamento
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP, -- Data de registro do orçamento
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE
);

-- Guarda múltiplos anexos de referência visual para a mesma ideia
CREATE TABLE Referencia_Visual (
    id_referencia INT AUTO_INCREMENT PRIMARY KEY, -- Identificador da foto de referência
    id_ideia INT NOT NULL,                       -- FK: Ideia à qual esta foto pertence
    caminho_imagem VARCHAR(255) NOT NULL,        -- URL ou caminho de armazenamento da imagem no servidor/S3
    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP, -- Data de envio do arquivo
    FOREIGN KEY (id_ideia) REFERENCES Ideia_Tatuagem(id_ideia) ON DELETE CASCADE
);

-- 4. AGENDAMENTO E SESSÕES

CREATE TABLE Agendamento (
    id_agendamento INT AUTO_INCREMENT PRIMARY KEY, -- Identificador da sessão na agenda
    id_cliente INT NOT NULL,                       -- FK: Cliente agendado
    id_tatuador INT NOT NULL,                      -- FK: Tatuador responsável pela sessão
    id_ideia INT NULL,                             -- FK (Opcional): Vincula a sessão a uma ideia/orçamento prévio
    data_hora_inicio DATETIME NOT NULL,            -- Data e horário de início da sessão
    data_hora_fim DATETIME NOT NULL,               -- Data e horário previstos para o término
    status ENUM('PENDENTE', 'CONFIRMADO', 'CANCELADO', 'REALIZADO') DEFAULT 'PENDENTE', -- Estado do agendamento
    descricao TEXT,                                -- Notas ou observações rápidas sobre o horário
    valor_final DECIMAL(10,2),                     -- Valor negociado/cobrado efetivamente pela sessão
    forma_pagamento VARCHAR(50),                   -- ex: Pix, Cartão de Crédito, Dinheiro
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_tatuador) REFERENCES Tatuador(id_tatuador) ON DELETE CASCADE,
    FOREIGN KEY (id_ideia) REFERENCES Ideia_Tatuagem(id_ideia) ON DELETE SET NULL
);


-- 5. LEMBRETES WHATSAPP 

CREATE TABLE Notificacao_Whatsapp (
    id_notificacao INT AUTO_INCREMENT PRIMARY KEY, -- Identificador do disparo de mensagem
    id_agendamento INT NOT NULL,                  -- FK: Agendamento vinculado à mensagem
    tipo ENUM('CONFIRMACAO', 'LEMBRETE_24H', 'POS_TATUAGEM') NOT NULL, -- Finalidade do aviso automatizado
    status_envio ENUM('PENDENTE', 'ENVIADO', 'FALHA') DEFAULT 'PENDENTE', -- Status da fila de envio da API
    data_programada DATETIME NOT NULL,            -- Momento exato em que a API deve disparar o WhatsApp
    data_envio DATETIME NULL,                     -- Momento real em que o WhatsApp confirmou a entrega
    mensagem TEXT,                                -- Conteúdo do texto enviado ao cliente
    FOREIGN KEY (id_agendamento) REFERENCES Agendamento(id_agendamento) ON DELETE CASCADE
);


-- 6. ANAMNESE E TERMO DE RESPONSABILIDADE 

CREATE TABLE Anamnese (
    id_anamnese INT AUTO_INCREMENT PRIMARY KEY,   -- Identificador da ficha de saúde
    id_cliente INT NOT NULL,                      -- FK: Cliente respondente
    id_agendamento INT NOT NULL,                  -- FK: Sessão específica à qual o termo está vinculado
    data_preenchimento DATETIME DEFAULT CURRENT_TIMESTAMP, -- Data e hora em que a ficha foi preenchida

    -- Respostas objetivas da condição de saúde do cliente
    possui_alergia BOOLEAN DEFAULT FALSE,         -- Possui algum tipo de alergia?
    descricao_alergia TEXT,                       -- Detalhes se possui_alergia = TRUE (ex: Pigmentos, Látex)
    possui_doenca_pele BOOLEAN DEFAULT FALSE,     -- Possui afecção de pele no local? (ex: Psoríase, Dermatite)
    descricao_doenca_pele TEXT,                   -- Detalhes das afecções de pele
    diabetico BOOLEAN DEFAULT FALSE,              -- É diabético? (Influencia na cicatrização)
    hemofilico BOOLEAN DEFAULT FALSE,             -- Possui problemas de coagulação sanguínea?
    cardiopata BOOLEAN DEFAULT FALSE,             -- É cardiopata?
    epileptico BOOLEAN DEFAULT FALSE,             -- Possui epilepsia?
    hipertenso BOOLEAN DEFAULT FALSE,             -- É hipertenso?
    faz_uso_medicamento BOOLEAN DEFAULT FALSE,    -- Usa algum remédio contínuo?
    descricao_medicamento TEXT,                   -- Nome dos medicamentos
    gestante BOOLEAN DEFAULT FALSE,               -- Está grávida ou lactante?
    ja_fez_tatuagem BOOLEAN DEFAULT FALSE,        -- Já fez tatuagem anteriormente?
    teve_reacao_tatuagem_anterior BOOLEAN DEFAULT FALSE, -- Teve problemas com cicatrização anterior?
    descricao_reacao TEXT,                        -- Detalhes da reação anterior
    consome_alcool_drogas BOOLEAN DEFAULT FALSE,  -- Consumiu álcool/drogas nas últimas 24h?
    usa_anticoagulante BOOLEAN DEFAULT FALSE,     -- Usa remédios que afinam o sangue?

    -- Consentimento Legal e Termo de Responsabilidade
    ciente_riscos BOOLEAN NOT NULL DEFAULT TRUE,  -- Confirmação de ciência dos riscos inerentes do procedimento
    termo_aceito BOOLEAN NOT NULL DEFAULT TRUE,   -- Aceite formal dos termos de responsabilidade
    observacoes TEXT,                             -- Notas extras do tatuador sobre o estado de saúde
    
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_agendamento) REFERENCES Agendamento(id_agendamento) ON DELETE CASCADE
);


-- 7. REGISTRO FOTOGRÁFICO E CICATRIZAÇÃO 
CREATE TABLE Foto_Sessao (
    id_foto INT AUTO_INCREMENT PRIMARY KEY,       -- Identificador da foto gravada no processo
    id_agendamento INT NOT NULL,                  -- FK: Sessão/Agendamento correspondente
    caminho_imagem VARCHAR(255) NOT NULL,          -- URL ou caminho do arquivo da foto salva
    tipo ENUM('ANTES', 'RESULTADO_RECENTE', 'CICATRIZACAO') NOT NULL, -- Etapa do processo fotográfico
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP, -- Data/hora do cadastro ou envio da foto
    observacao TEXT,                              -- Notas do tatuador (ex: "30 dias pós-sessão, sem falhas")
    FOREIGN KEY (id_agendamento) REFERENCES Agendamento(id_agendamento) ON DELETE CASCADE
);

-- 8. MATERIAIS E CONSUMO DA SESSÃO

-- Cadastro e controle do estoque de insumos do tatuador autônomo
CREATE TABLE Material (
    id_material INT AUTO_INCREMENT PRIMARY KEY,   -- Identificador do item de estoque
    id_tatuador INT NOT NULL,                     -- FK: Tatuador proprietário do material
    nome VARCHAR(100) NOT NULL,                   -- Nome do insumo (ex: "Tinta Dynamic Black", "Agulha 03RL")
    categoria ENUM('TINTA', 'AGULHA', 'DESCARTAVEL', 'HIGIENE', 'OUTROS') NOT NULL, -- Classificação
    quantidade_estoque DECIMAL(10,2) NOT NULL DEFAULT 0, -- Saldo atual disponível no estoque
    unidade_medida VARCHAR(20) NOT NULL,          -- ex: 'ml', 'unidade', 'caixa', 'pacote'
    FOREIGN KEY (id_tatuador) REFERENCES Tatuador(id_tatuador) ON DELETE CASCADE
);

-- Tabela associativa (N:M): Relatório detalhado dos materiais gastos por sessão
CREATE TABLE Material_Sessao (
    id_material_sessao INT AUTO_INCREMENT PRIMARY KEY, -- Identificador do registro de uso
    id_agendamento INT NOT NULL,                       -- FK: Sessão/Agendamento onde o material foi usado
    id_material INT NOT NULL,                          -- FK: Material retirado do estoque
    quantidade_usada DECIMAL(10,2) NOT NULL,           -- Quantidade consumida no procedimento (ex: 5.00 ml)
    FOREIGN KEY (id_agendamento) REFERENCES Agendamento(id_agendamento) ON DELETE CASCADE,
    FOREIGN KEY (id_material) REFERENCES Material(id_material) ON DELETE CASCADE
);


-- 9. PORTFÓLIO DO TATUADOR

CREATE TABLE Portfolio (
    id_portfolio INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador do item do portfólio
    id_tatuador INT NOT NULL,                     -- FK: Tatuador dono do trabalho
    titulo VARCHAR(100) NOT NULL,                 -- Título da obra (ex: "Fechamento de Costas Oriental")
    descricao TEXT,                               -- Descrição técnica ou artística da arte
    caminho_imagem VARCHAR(255) NOT NULL,         -- URL ou caminho de armazenamento da imagem do trabalho
    estilo VARCHAR(50),                           -- Estilo do trabalho (ex: "Realismo", "Tribal")
    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP, -- Data de publicação da foto no portfólio
    ordem_exibicao INT DEFAULT 0,                 -- Posição para ordenação de exibição no perfil público
    FOREIGN KEY (id_tatuador) REFERENCES Tatuador(id_tatuador) ON DELETE CASCADE
);


