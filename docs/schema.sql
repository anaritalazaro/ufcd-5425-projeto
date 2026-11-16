-- Fornada · Sobra Zero — esquema da base de dados (PostgreSQL 18)
-- Modelo E-R v.1 (04/11/2026), completado com as restrições do dicionário de
-- dados (UFCD 10790, Sprint 3, secção 2.3). Sub-issue #13.
--
-- Origem de cada restrição, indicada nos comentários:
--   [DD]           dicionário de dados do Sprint 3 (UFCD 10790)
--   [RNxx]         regra de negócio (Sprint 2; RN12 e RN13 no Sprint 3)
--   [RFxx]         critério de aceitação de um requisito (Sprint 3, secção 1.5)
--   [Sebenta 5425] sebenta da UFCD 5425, com a secção
--   [Prop]         proposta, registada em docs/decisoes.md
--
-- Ordem: tabelas PAI antes das tabelas FILHO, para que cada chave estrangeira
-- aponte para uma tabela que já existe. As chaves estrangeiras ficam dentro do
-- CREATE TABLE, por isso o script pode correr outra vez sem erro (IF NOT EXISTS,
-- como na sebenta da UFCD 5425, secção 7.3).
--
-- Chaves estrangeiras: ON DELETE RESTRICT em todas. Nada com histórico se apaga,
-- fica inativo (RN11); a base de dados recusa apagar um registo que outro use.


CREATE TABLE IF NOT EXISTS utilizador (
	id_utilizador SERIAL PRIMARY KEY,
	nome VARCHAR(120) NOT NULL
		CONSTRAINT ck_utilizador_nome
			CHECK(length(trim(nome)) > 0),                              -- [Sebenta 5425, 7.3]
	email VARCHAR(255) NOT NULL UNIQUE,                                  -- [DD] RF10
	hash_palavra_passe VARCHAR(255) NOT NULL,                            -- [DD] RNF07: só o hash
	perfil VARCHAR(30) NOT NULL
		CONSTRAINT ck_utilizador_perfil 
			CHECK(perfil IN ('administrador', 'producao', 'balcao')),   -- [DD] RF12
	ativo BOOLEAN NOT NULL DEFAULT true                                  -- [DD] RN11, RF11
);

CREATE TABLE IF NOT EXISTS produto (
	id_produto SERIAL PRIMARY KEY,
	nome VARCHAR(120) NOT NULL UNIQUE                                    -- [DD] RN01
		CONSTRAINT ck_produto_nome 
			CHECK(length(trim(nome)) > 0),                              -- [RN01] obrigatório; [Sebenta 5425, 7.3]
	categoria VARCHAR(60) NOT NULL,
	preco_venda DECIMAL(10,2) NOT NULL 
		CONSTRAINT ck_produto_preco_venda 
			CHECK(preco_venda >= 0),                                     -- [DD] RN01
	validade_horas INTEGER NOT NULL 
		CONSTRAINT ck_produto_validade_horas
			CHECK(validade_horas > 0),                                   -- [DD] RN08
	conservacao VARCHAR(20) NOT NULL
		CONSTRAINT ck_produto_conservacao
			CHECK (conservacao IN ('ambiente', 'refrigerado', 'congelado')),    -- [Prop]
	ativo BOOLEAN NOT NULL DEFAULT true,                                 -- [DD] RN11
	rendimento_lote INTEGER NOT NULL 
		CONSTRAINT ck_produto_rendimento_lote
			CHECK(rendimento_lote > 0)                                   -- [DD] RN03, critério do RF03
);

CREATE TABLE IF NOT EXISTS materia_prima (
	id_materia_prima SERIAL PRIMARY KEY,
	nome VARCHAR(120) NOT NULL UNIQUE                                    -- [DD] RN01
		CONSTRAINT ck_materia_prima_nome 
			CHECK(length(trim(nome)) > 0),                               -- [RN01] obrigatório; [Sebenta 5425, 7.3]
	unidade VARCHAR(2) NOT NULL 
		CONSTRAINT ck_materia_prima_unidade
			CHECK(unidade IN ('g', 'ml', 'un')),                         -- [DD] RN02
	stock_atual DECIMAL(12,3) NOT NULL DEFAULT 0 
		CONSTRAINT ck_materia_prima_stock_atual
			CHECK(stock_atual >= 0),                                     -- [DD] RN05
	stock_minimo DECIMAL(12,3) NOT NULL DEFAULT 0 
		CONSTRAINT ck_materia_prima_stock_minimo
			CHECK(stock_minimo >= 0),                                    -- [DD]
	custo_unitario DECIMAL(12,6) NOT NULL
		CONSTRAINT ck_materia_prima_custo_unitario
			CHECK (custo_unitario >= 0),                                 -- [DD] RN01; precisão (12,6) [Prop]
	alergenios TEXT,
	ativo BOOLEAN NOT NULL DEFAULT true                                  -- [DD] RN11
);

CREATE TABLE IF NOT EXISTS equipamento (
	id_equipamento SERIAL PRIMARY KEY,
	nome VARCHAR(120) NOT NULL UNIQUE,                                   -- [DD] RN01
	tipo VARCHAR(20) NOT NULL,
	temperatura_minima DECIMAL(5,2) NOT NULL,
	temperatura_maxima DECIMAL(5,2) NOT NULL,
	ativo BOOLEAN NOT NULL DEFAULT true,                                 -- [DD] RN11
	CONSTRAINT ck_equipamento_nome
		CHECK (length(trim(nome)) > 0),                                  -- [RN01] obrigatório; [Sebenta 5425, 7.3]
	CONSTRAINT ck_equipamento_temperaturas
		CHECK (temperatura_minima < temperatura_maxima)                  -- [DD] critério do RF05	
);



CREATE TABLE IF NOT EXISTS receita_ficha_tecnica (
	id_produto INTEGER NOT NULL,
	id_materia_prima INTEGER NOT NULL,
	quantidade_para_rendimento DECIMAL(12,3) NOT NULL,                  
	PRIMARY KEY(id_produto, id_materia_prima),                           -- [DD] RN03: cada matéria-prima aparece uma só vez na receita          
	CONSTRAINT ck_receita_quantidade
		CHECK(quantidade_para_rendimento > 0),                           -- [DD] RN02, RN04
	CONSTRAINT fk_receita_id_produto_produto
		FOREIGN KEY (id_produto) REFERENCES produto (id_produto)
		ON DELETE RESTRICT,
	CONSTRAINT fk_receita_id_materia_prima_materia_prima
		FOREIGN KEY (id_materia_prima) REFERENCES materia_prima (id_materia_prima)
		ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS lote_producao (
	id_lote SERIAL PRIMARY KEY,
	id_produto INTEGER NOT NULL,
	id_equipamento INTEGER,                                               -- [DD] obrigatório a partir da fase das temperaturas
	id_utilizador INTEGER,                                                -- [DD] obrigatório a partir da fase da autenticação
	lote VARCHAR(40) NOT NULL UNIQUE,                                     -- [DD] RN06: um lote só é registado uma vez
	data_hora_producao TIMESTAMP NOT NULL,
	turno VARCHAR(20) NOT NULL
		CONSTRAINT ck_lote_turno
			CHECK(turno IN ('manhã', 'tarde')),                               -- [DD] RN12
	qtd_planeada INTEGER
		CONSTRAINT ck_lote_qtd_planeada
			CHECK(qtd_planeada >= 0),                                         -- [DD]
	qtd_produzida INTEGER NOT NULL 
		CONSTRAINT ck_lote_qtd_produzida
			CHECK(qtd_produzida > 0),                                         -- [DD]   
	qtd_vendida INTEGER                                                   -- [DD] preenchida no fecho (RN10)
		CONSTRAINT ck_lote_qtd_vendida
			CHECK(qtd_vendida >= 0),                                          -- [DD] RN10
	qtd_desperdicada INTEGER                                              -- [DD] preenchida no fecho (RN10)
		CONSTRAINT ck_lote_qtd_desperdicada
			CHECK(qtd_desperdicada >= 0),                                     -- [DD] RN10
	validade TIMESTAMP NOT NULL,
	estado VARCHAR(20) NOT NULL DEFAULT 'aberto'                          -- [DD] RN13: aberto desde o registo
		CONSTRAINT ck_lote_estado
			CHECK(estado IN ('aberto', 'fechado', 'rejeitado')),              -- [DD] RN13
	-- [DD] RN10, critério do RF07: um lote fechado tem as quantidades do fecho
	-- preenchidas e produzido = vendido + desperdiçado. Os IS NOT NULL são
	-- necessários: com uma quantidade em falta, a soma dá NULL e o CHECK aceitaria.
	CONSTRAINT ck_lote_fecho
		CHECK (
			estado <> 'fechado'                                            -- ou o lote não está fechado (e então não se exige nada)
			OR (                                                           -- ou, se está fechado, as três condições do parêntese têm de ser todas verdadeiras
				qtd_vendida IS NOT NULL                                    
				AND qtd_desperdicada IS NOT NULL
				AND qtd_vendida + qtd_desperdicada = qtd_produzida
			)
		),
	-- [Prop] a validade é posterior à produção (validade_horas > 0, RN08).
	-- O cálculo exato depende do produto e ficará no domínio: 
	-- Lote.calcularValidade() (Sprint 3, diagrama de classes, secção 2.4).
	CONSTRAINT ck_lote_validade
		CHECK (validade > data_hora_producao),
	CONSTRAINT fk_lote_producao_id_produto_produto
		FOREIGN KEY (id_produto) REFERENCES produto (id_produto)
		ON DELETE RESTRICT,
	CONSTRAINT fk_lote_producao_id_equipamento_equipamento
		FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento)
		ON DELETE RESTRICT,
	CONSTRAINT fk_lote_producao_id_utilizador_utilizador
		FOREIGN KEY (id_utilizador) REFERENCES utilizador (id_utilizador)
		ON DELETE RESTRICT
);                        

CREATE TABLE IF NOT EXISTS registo_temperatura (
	id_registo SERIAL PRIMARY KEY,
	id_equipamento INTEGER NOT NULL,
	id_utilizador INTEGER,                                                 -- [DD] obrigatório a partir da fase da autenticação
	data_hora TIMESTAMP NOT NULL,
	turno VARCHAR(20) NOT NULL,
	temperatura DECIMAL(5,2) NOT NULL,
	conforme BOOLEAN NOT NULL,                                             -- [DD] RN09: falso numa ocorrência
	acao_corretiva TEXT,
	CONSTRAINT ck_registo_turno
		CHECK (turno IN ('manhã', 'tarde')),                               -- [DD] RN12
	-- [DD] RN09, critério do RF06: numa ocorrência, a ação corretiva é obrigatória e não pode ficar em branco [Sebenta 5425, 7.3]. 
	-- Saber se a leitura está fora dos limites compara duas tabelas, por isso fica no domínio:
	-- Equipamento.eOcorrencia() e RegistoTemperatura.validar().
	-- O IS NOT NULL é necessário: length(trim(NULL)) dá NULL e o CHECK aceitaria.
	CONSTRAINT ck_registo_acao_corretiva
		CHECK (
			conforme
			OR (acao_corretiva IS NOT NULL AND length(trim(acao_corretiva)) > 0)
		),
	CONSTRAINT fk_registo_temperatura_id_equipamento_equipamento
		FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento)
		ON DELETE RESTRICT,
	CONSTRAINT fk_registo_temperatura_id_utilizador_utilizador
		FOREIGN KEY (id_utilizador) REFERENCES utilizador (id_utilizador)
		ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS movimento_stock (
	id_movimento SERIAL PRIMARY KEY,
	id_materia_prima INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL 
		CONSTRAINT ck_movimento_tipo
			CHECK(tipo IN ('entrada', 'ajuste', 'consumo')),    -- [DD]
	quantidade DECIMAL(12,3) NOT NULL,
	quantidade_contada DECIMAL(12,3)
		CONSTRAINT ck_movimento_contada_positiva
			CHECK (quantidade_contada >= 0),                 -- [RN01] quantidades não negativas
	id_lote INTEGER,
	data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	id_utilizador INTEGER,                                   -- [DD] obrigatório a partir da fase da autenticação
    -- [DD] RN07: entrada e consumo positivos (o tipo indica o sentido);
	-- no ajuste, a diferença aplicada, nunca 0 (uma contagem igual não gera ajuste).
	CONSTRAINT ck_movimento_quantidade
		CHECK (
			(tipo IN ('entrada', 'consumo') AND quantidade > 0)    -- parte 1: positivos
			OR (tipo = 'ajuste' AND quantidade <> 0)               -- parte 2: diferença, nunca 0
		),
	-- [DD] RN07: quantidade contada obrigatória no ajuste e vazia nos outros tipos
	CONSTRAINT ck_movimento_contada
		CHECK ((tipo = 'ajuste') = (quantidade_contada IS NOT NULL)),
	-- [DD] RN06: lote obrigatório no consumo e vazio nos outros tipos
	CONSTRAINT ck_movimento_lote
		CHECK ((tipo = 'consumo') = (id_lote IS NOT NULL)),
	-- [DD] RN06: um só consumo de cada matéria-prima por lote. No PostgreSQL os
	-- NULL são distintos por omissão, por isso as entradas e os ajustes
	-- (id_lote vazio) não entram em conflito entre si.
	CONSTRAINT uq_movimento_lote_materia
		UNIQUE (id_lote, id_materia_prima),
	CONSTRAINT fk_movimento_stock_id_materia_prima_materia_prima
		FOREIGN KEY (id_materia_prima) REFERENCES materia_prima (id_materia_prima)
		ON DELETE RESTRICT,
	CONSTRAINT fk_movimento_stock_id_lote_lote_producao
		FOREIGN KEY (id_lote) REFERENCES lote_producao (id_lote)
		ON DELETE RESTRICT,
	CONSTRAINT fk_movimento_stock_id_utilizador_utilizador
		FOREIGN KEY (id_utilizador) REFERENCES utilizador (id_utilizador)
		ON DELETE RESTRICT
);