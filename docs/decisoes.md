# Decisões do projeto
 
Este documento regista as decisões tomadas depois da aprovação da entrega inicial, em resposta aos comentários do formador e validadas com o mesmo.
 
## 1. Prioridades da primeira versão
 
A primeira versão concentra-se num percurso pequeno e consistente:
 
> receita → produção do lote → consumo de matérias-primas → fecho com vendido e desperdiçado
 
**Núcleo (primeira versão):**
 
- Gestão de produtos, matérias-primas e receitas
- Entrada e ajuste de stock das matérias-primas
- Registo da produção de um lote, com consumo automático das matérias-primas
- Fecho do dia com as quantidades vendidas e desperdiçadas

**Fases seguintes, só depois de o núcleo estar a funcionar:**
 
1. Plano do dia e cálculo antecipado das necessidades
2. Registo das temperaturas dos equipamentos e sinalização das ocorrências
3. Segurança: validação completa, tratamento de erros e proteção dos formulários
4. Autenticação, acesso por várias pessoas e perfis de utilizador
5. Rejeição automática de lotes por temperatura
6. Melhorias visuais (CSS)

Durante a demonstração local, o utilizador é opcional nos registos. Passa a ser obrigatório na fase da autenticação.
 
## 2. Gestão de stock
 
As compras ficam fora do sistema. O stock é registado numa única tabela de movimentos, `movimento_stock`, com três tipos:
 
| Movimento | Quando acontece | O que o utilizador introduz | Efeito no stock |
| --- | --- | --- | --- |
| Entrada | Stock inicial e cada reposição | A quantidade recebida | Soma a quantidade |
| Ajuste | Correção após contagem física | A quantidade encontrada na contagem | Passa a ser a quantidade contada |
| Consumo | Automático, ao registar um lote | Nada: é calculado pela receita | Subtrai as quantidades consumidas |
 
**Ajustes.** O utilizador introduz a **quantidade encontrada na contagem**, que é o que tem à frente quando conta o stock. O sistema calcula a diferença face ao stock atual e guarda as duas: a quantidade contada e a diferença aplicada (positiva ou negativa). Uma contagem igual ao stock atual não gera movimento.
 
**Consumos.** Cada movimento de consumo fica associado ao lote que o originou. Um lote só pode ser registado uma vez, e a base de dados não aceita dois consumos da mesma matéria-prima para o mesmo lote, por isso repetir o registo não desconta as matérias-primas duas vezes.
 
**Transações.** Cada operação é gravada por inteiro ou não é gravada:
 
- uma entrada ou ajuste grava o movimento e atualiza o stock na mesma transação;
- o registo de um lote cria o lote, grava os consumos e atualiza o stock na mesma transação. Se faltar stock de alguma matéria-prima, nada fica guardado.
O stock inicial é registado como uma entrada.
 
## 3. Receitas e quantidades
 
As quantidades da receita são definidas **para uma quantidade-base de produção**, como numa ficha técnica. Cada produto tem um **rendimento do lote**: o número de unidades que a receita produz.
 
Cada matéria-prima tem **uma unidade-base**, igual no stock e na receita: `g`, `ml` ou `un`. Não há conversões automáticas; as entradas são introduzidas já nessa unidade.
 
Exemplo, a partir de uma ficha técnica do produto **pastel de nata** (rendimento do lote: 100 unidades):
 
| Matéria-prima | Unidade | Quantidade para 100 pastéis |
| --- | --- | --- |
| Farinha de trigo T55 | g | 1 505 |
| Leite gordo | ml | 1 785 |
| Açúcar branco | g | 1 070 |
| Margarina para folhados | g | 905 |
| Água | ml | 1 440 |
| Ovos (gemas) | un | 22 |
| Sal fino | g | 15 |
| Limão (casca) | un | 7 |
| Canela em pau | un | 7 |
 
O consumo é calculado proporcionalmente à **quantidade efetivamente produzida**:
 
> consumo = (quantidade produzida ÷ rendimento do lote) × quantidade da receita
> farinha para 60 pastéis = (60 ÷ 100) × 1 505 g = 903 g
 
Simplificações da primeira versão:
 
- As sub-receitas (massa folhada e creme) são juntas numa só receita. Uma matéria-prima usada nas duas, como a farinha (1 360 g + 145 g), fica numa só linha.
- Os ingredientes sem quantidade definida («q.b.», como a canela em pó) ficam fora da receita e do controlo de stock.

## 4. Fecho do dia
 
No fecho do dia, toda a quantidade produzida fica distribuída entre vendido e desperdiçado. O sistema valida que:
 
- as quantidades vendida e desperdiçada não são negativas;
- produzido = vendido + desperdiçado.

Não há transição de produto para o dia seguinte. É uma política da casa: a pastelaria de fabrico próprio vende só no próprio dia. 
A ficha técnica de referência do pastel de nata admite conservação até 24 h a 2–8 °C, por isso a transição de produtos ainda dentro da validade fica identificada como evolução futura deste projeto.
 
## 5. Temperaturas
 
A rejeição automática de lotes fica para uma fase posterior. Na fase das temperaturas, o sistema:
 
- regista a temperatura de cada equipamento, com data, hora e turno;
- assinala como **ocorrência** qualquer registo abaixo da temperatura mínima ou acima da máxima do equipamento (por exemplo, 2–8 °C numa câmara frigorífica, como indica a ficha técnica de referência);
- obriga a indicar a ação corretiva numa ocorrência;
- lista as ocorrências, para consulta.

O controlo das temperaturas de cozedura fica também como evolução futura.

## 6. Dependências da aplicação

As dependências estão em `requirements.txt`:

| Biblioteca | Para que serve | Porquê esta |
| --- | --- | --- |
| `flask` | Framework web: recebe os pedidos e devolve as páginas | Stack validada pelo formador; leve, sem estrutura imposta, o que deixa as camadas visíveis |
| `psycopg[binary]` | Driver que liga o Python ao PostgreSQL | Driver mais usado para PostgreSQL, com consultas parametrizadas; permite escrever o SQL à mão. A variante `binary` evita erros de compilação no Windows |
| `python-dotenv` | Lê o ficheiro `.env` com as credenciais | O enunciado exige credenciais fora do código; o `config.py` lê-as depois com `os.getenv()` |

A sebenta usa SQLite, acedido com o módulo `sqlite3` incluído no Python, e lê a configuração com `os.getenv()`. Como este projeto usa PostgreSQL e um ficheiro `.env`, foram precisos um driver para o PostgreSQL (psycopg) e uma biblioteca para ler o `.env` (python-dotenv).

Alternativas postas de lado: psycopg2 (versão anterior do driver) e SQLAlchemy (gera o SQL automaticamente e esconderia o SQL que é avaliado).

## 7. Base de dados em Docker

Nesta fase, o Docker corre só o PostgreSQL. A aplicação Flask corre diretamente no computador, com `python -m flask --app main run --debug`.

**Versão.** O contentor usa o PostgreSQL 18, a versão instalada e usada na UFCD 10788, que o pgAdmin já suporta. A versão fica fixa no `docker-compose.yml`, para que todos os computadores usem a mesma, independentemente do PostgreSQL que tenham instalado.

**Porta.** O contentor fica acessível na porta **5433** do computador. Dentro do contentor, o PostgreSQL usa a porta habitual, 5432; o Docker liga uma à outra.

| Serviço | Onde corre | Porta no computador |
| --- | --- | --- |
| PostgreSQL do projeto (versão 18) | Contentor Docker | 5433 |
| PostgreSQL local (de outras UFCD) | Serviço do Windows | 5432 |

O computador de desenvolvimento já tem um PostgreSQL instalado como serviço do Windows, que arranca sozinho e ocupa a porta 5432 (confirmado com `netstat -ano`). A porta 5433 evita o conflito sem parar nem desinstalar esse serviço. Como o formador e os colegas também usaram o PostgreSQL na UFCD 10788, é provável que tenham o mesmo conflito, e a porta 5433 evita-o também nos seus computadores.

Alternativa posta de lado: parar o serviço local antes de cada sessão. Obrigaria a mexer nos serviços do Windows, com permissões de administrador, e o conflito voltaria a cada reinício, porque o serviço arranca automaticamente.

**Ligações.** A aplicação e o pgAdmin ligam-se a `localhost:5433`, com as credenciais do `.env` (`POSTGRES_PORT=5433`).