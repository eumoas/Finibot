# Prompt para alteração no Fini

Cole o texto abaixo no Claude Code, na raiz do repositório do Fini.

---

## Contexto

O Fini é um chatbot educacional de finanças pessoais no Telegram, voltado a estudantes do Ensino Médio, construído em FastAPI + PostgreSQL + Redis. Ele faz parte de um trabalho acadêmico cujo pano de fundo é a ludopatia entre jovens, tratada como problema de saúde pública.

Uma revisão pedagógica identificou uma contradição no produto: o sistema de gamificação usa uma mecânica de sequência diária (streak) que zera quando o usuário deixa um dia sem registrar. Essa mecânica opera por aversão à perda e otimiza o retorno diário ao aplicativo, não o comportamento pedagógico que o produto quer promover. Ela é estruturalmente parecida com as mecânicas de engajamento usadas por plataformas de aposta, o que é inaceitável em uma ferramenta que discute justamente esse tema com adolescentes.

As demais mecânicas de gamificação (pontos de razão fixa, níveis de progressão, desafios semanais) foram avaliadas e não apresentam o mesmo problema: recompensam ação deliberada e declarada, não resultado incerto, e não há nada que se perca. Elas permanecem.

## Objetivo

Substituir a mecânica de streak por uma mecânica de constância acumulativa que nunca decresce, e auditar o restante do código em busca de outros padrões de punição ou de reforço em razão variável.

## Tarefa 1: substituir o streak por constância acumulativa

Regra atual a ser removida (RN-03): a sequência de 7 dias exige pelo menos 1 lançamento por dia e a interrupção zera o contador.

Regra nova:

- Manter um contador de **dias com registro no mês corrente** e um contador de **total de dias com registro desde o início do uso**. Ambos só aumentam.
- Nenhum dos dois zera por inatividade. A virada de mês inicia uma nova contagem mensal, mas o total acumulado nunca é reiniciado.
- Os marcos de reconhecimento passam a ser cumulativos e não consecutivos: 7, 15, 30 e 60 dias com registro. Cada marco é concedido uma única vez e não é perdido depois de concedido.
- Remover qualquer lógica de reset, decaimento, expiração ou penalidade associada a inatividade.

## Tarefa 2: renomear o conceito

Substituir o termo `streak` em todo o código, no banco, nas chaves de Redis e nas mensagens ao usuário. Usar `constancia` (sem acento) em identificadores e `constância` no texto exibido.

Pontos a alterar:

- Campo `streak` na tabela `users` (criar migration Alembic com renomeação e os novos campos, preservando os dados existentes: o valor atual do streak vira o total acumulado).
- Chaves de Redis usadas para controle de streak.
- Nomes de funções, variáveis e testes.
- Toda cópia de texto exibida ao usuário.

## Tarefa 3: revisar a cópia das mensagens

Remover das mensagens ao usuário qualquer formulação que:

- alerte sobre perda iminente de progresso ("você vai perder sua sequência", "faltam X horas");
- crie urgência artificial ou pressão de retorno;
- use metáforas de "chama", "fogo", "não quebre a corrente" ou equivalentes.

Substituir por reconhecimento do que já foi feito, sem projeção de perda. Exemplo do tom desejado: em vez de "não perca sua sequência de 6 dias", usar "você já registrou em 6 dias este mês".

Revisar também as mensagens de notificação e lembrete, se existirem: elas não devem convocar o retorno pela perda, e sim informar o estado atual.

## Tarefa 4: auditoria do restante do sistema

Percorrer o código de gamificação (pontos, níveis, desafios semanais, notificações) e reportar, sem alterar antes de eu confirmar, qualquer ocorrência de:

- recompensa em razão variável, ou seja, com valor ou probabilidade incertos;
- qualquer contador, saldo ou status que possa diminuir por ação ou inatividade do usuário;
- limite de tempo para concluir uma ação sob pena de perda;
- mensagens de quase-ganho ("faltou pouco", "você quase conseguiu").

Confirmar explicitamente se a regra RN-02, segundo a qual pontos nunca diminuem, está de fato implementada em todos os caminhos do código.

## Tarefa 5: documentação

Atualizar a especificação de requisitos com a nova regra de negócio no lugar da RN-03, e registrar em um comentário no módulo de gamificação o critério de design adotado: **nenhuma mecânica do Fini pode operar por aversão à perda ou por recompensa incerta.**

## Entregáveis

1. Migration Alembic.
2. Alterações de código e testes.
3. Diff da cópia de mensagens.
4. Relatório da auditoria da Tarefa 4, em lista, com arquivo e linha de cada ocorrência encontrada.
