CREATE TABLE IF NOT EXISTS "utilizador" (
	"id_utilizador" SERIAL,
	"nome" VARCHAR(120) NOT NULL,
	"email" VARCHAR(255) NOT NULL UNIQUE,
	"hash_palavra_passe" VARCHAR(255) NOT NULL,
	"perfil" VARCHAR(30) NOT NULL CHECK(perfil IN ('administrador', 'producao', 'balcao')),
	"ativo" BOOLEAN NOT NULL DEFAULT true,
	PRIMARY KEY("id_utilizador")
);

CREATE TABLE IF NOT EXISTS "produto" (
	"id_produto" SERIAL,
	"nome" VARCHAR(120) NOT NULL UNIQUE,
	"categoria" VARCHAR(60) NOT NULL,
	"preco_venda" DECIMAL(10,2) NOT NULL CHECK(preco_venda >= 0),
	"validade_horas" INTEGER NOT NULL CHECK(validade_horas > 0),
	"conservacao" VARCHAR(10) NOT NULL,
	"ativo" BOOLEAN NOT NULL DEFAULT true,
	"rendimento_lote" INTEGER NOT NULL CHECK(rendimento_lote > 0),
	PRIMARY KEY("id_produto")
);

CREATE TABLE IF NOT EXISTS "materia_prima" (
	"id_materia_prima" SERIAL,
	"nome" VARCHAR(120) NOT NULL UNIQUE,
	"unidade" VARCHAR(2) NOT NULL CHECK(unidade IN ('g', 'ml', 'un')),
	"stock_atual" DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK(stock_atual >= 0),
	"stock_minimo" DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK(stock_minimo >= 0),
	"custo_unitario" DECIMAL(10,4) NOT NULL,
	"alergenios" TEXT,
	"ativo" BOOLEAN NOT NULL DEFAULT true,
	PRIMARY KEY("id_materia_prima")
);

CREATE TABLE IF NOT EXISTS "receita_ficha_tecnica" (
	"id_produto" INTEGER NOT NULL,
	"id_materia_prima" INTEGER NOT NULL,
	"quantidade_para_rendimento" DECIMAL(12,3) NOT NULL CHECK(quantidade_para_rendimento > 0),
	PRIMARY KEY("id_produto", "id_materia_prima")
);

CREATE TABLE IF NOT EXISTS "equipamento" (
	"id_equipamento" SERIAL,
	"nome" VARCHAR(120) NOT NULL,
	"tipo" VARCHAR(20) NOT NULL,
	"temperatura_maxima" DECIMAL(5,2) NOT NULL,
	"ativo" BOOLEAN NOT NULL DEFAULT true,
	"temperatura_minima" DECIMAL(5,2) NOT NULL,
	PRIMARY KEY("id_equipamento")
);

CREATE TABLE IF NOT EXISTS "lote_producao" (
	"id_lote" SERIAL,
	"id_produto" INTEGER NOT NULL,
	"id_equipamento" INTEGER,
	"id_utilizador" INTEGER,
	"lote" VARCHAR(40) NOT NULL UNIQUE,
	"data_hora_producao" TIMESTAMP NOT NULL,
	"turno" VARCHAR(20) NOT NULL CHECK(turno IN ('manha', 'tarde')),
	"qtd_planeada" INTEGER DEFAULT 0 CHECK(qtd_planeada >= 0),
	"qtd_produzida" INTEGER NOT NULL DEFAULT 0 CHECK(qtd_produzida >= 0),
	"qtd_vendida" INTEGER DEFAULT 0 CHECK(qtd_vendida >= 0),
	"qtd_desperdicada" INTEGER DEFAULT 0 CHECK(qtd_desperdicada >= 0),
	"validade" TIMESTAMP NOT NULL,
	"estado" VARCHAR(20) NOT NULL DEFAULT 'aberto' CHECK(estado IN ('aberto', 'fechado', 'rejeitado')),
	PRIMARY KEY("id_lote")
);

CREATE TABLE IF NOT EXISTS "registo_temperatura" (
	"id_registo" SERIAL,
	"id_equipamento" INTEGER NOT NULL,
	"id_utilizador" INTEGER,
	"data_hora" TIMESTAMP NOT NULL,
	"turno" VARCHAR(20) NOT NULL CHECK(turno IN ('manha', 'tarde')),
	"temperatura" DECIMAL(5,2) NOT NULL,
	"conforme" BOOLEAN NOT NULL,
	"acao_corretiva" TEXT,
	PRIMARY KEY("id_registo")
);

CREATE TABLE IF NOT EXISTS "movimento_stock" (
	"id_movimento" SERIAL NOT NULL,
	"id_materia_prima" INTEGER NOT NULL UNIQUE,
	"tipo" VARCHAR(20) NOT NULL CHECK(tipo IN ('entrada', 'ajuste', 'consumo')),
	"quantidade" DECIMAL(12,3) NOT NULL,
	"quantidade_contada" DECIMAL(12,3),
	"id_lote" INTEGER UNIQUE,
	"data_hora" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"id_utilizador" INTEGER,
	PRIMARY KEY("id_movimento")
);

ALTER TABLE "receita_ficha_tecnica"
ADD FOREIGN KEY("id_produto") REFERENCES "produto"("id_produto")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "receita_ficha_tecnica"
ADD FOREIGN KEY("id_materia_prima") REFERENCES "materia_prima"("id_materia_prima")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "lote_producao"
ADD FOREIGN KEY("id_produto") REFERENCES "produto"("id_produto")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "lote_producao"
ADD FOREIGN KEY("id_equipamento") REFERENCES "equipamento"("id_equipamento")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "lote_producao"
ADD FOREIGN KEY("id_utilizador") REFERENCES "utilizador"("id_utilizador")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "registo_temperatura"
ADD FOREIGN KEY("id_equipamento") REFERENCES "equipamento"("id_equipamento")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "registo_temperatura"
ADD FOREIGN KEY("id_utilizador") REFERENCES "utilizador"("id_utilizador")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "movimento_stock"
ADD FOREIGN KEY("id_materia_prima") REFERENCES "materia_prima"("id_materia_prima")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "movimento_stock"
ADD FOREIGN KEY("id_lote") REFERENCES "lote_producao"("id_lote")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "movimento_stock"
ADD FOREIGN KEY("id_utilizador") REFERENCES "utilizador"("id_utilizador")
ON UPDATE NO ACTION ON DELETE NO ACTION;