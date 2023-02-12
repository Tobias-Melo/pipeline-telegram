Pipeline de Dados | Telegram
Este é um projeto desenvolvido com objetivos de estudo, desenvolvido durante o curso 'Analista de Dados'.

Aluno Tobias Melo
Professor André Perez

Tópicos
Introdução;
Arquitetura;
Dados;
Análise Exploratória de Dados.
1. Introdução
Neste projeto desenvolveremos uma aplicação capaz de ingerir informações de um grupo do Telegram através de um chatbot, essa aplicação contará com um pipeline de dados completo.

O Telegram permite que as mensagens enviadas ao bot podem ser capturadas até mesmo no privado, mas restringimos a opção e utilizaremos o bot em um grupo.

1.1. Chatbot
Um chatbot é um programa de computador projetado para simular uma conversa com humanos, geralmente através de meios de comunicação baseados em texto ou voz. Eles são usados ​​em uma variedade de aplicações, como atendimento ao cliente, comércio eletrônico, entretenimento e muito mais.

Exemplos de chatbots incluem:
Um assistente de atendimento ao cliente que pode responder perguntas comuns sobre uma empresa e ajudar a encaminhar clientes para o departamento apropriado.
Um assistente virtual para um comércio eletrônico que pode recomendar produtos e ajudar os clientes a navegar pelo site.
Um chatbot de entretenimento que pode contar piadas ou responder perguntas sobre celebridades ou eventos esportivos.
1.2. Telegram
Telegram é uma plataforma de mensagens instantâneas baseada na nuvem que permite aos usuários enviar mensagens de texto, fotos, vídeos e arquivos de maneira segura e rápida. Ele foi fundado em 2013 por Pavel Durov, o criador da popular rede social russa VKontakte. Telegram tem sido elogiado por sua segurança e privacidade, e rapidamente ganhou milhões de usuários em todo o mundo. É muito popular entre desenvolvedores por ser pioneiro na implantação da funcionalidade de criação de chatbots, que, por sua vez, permitem a criação de diversas automações.

1.3. AWS
Amazon Web Services (AWS) é um conjunto de serviços de nuvem empresarial oferecido pela Amazon. Ele oferece uma variedade de serviços, incluindo computação em nuvem, armazenamento, banco de dados, análise e muito mais. Ele permite que as empresas escalem seus recursos de acordo com as necessidades do negócio e pagam apenas pelo que usam. Neste projeto a AWS será responsável por todo o mapeamento dos processos, desde a captação dos dados até a entrega final.

2. Arquitetura
Neste tópico, evidenciarei como será toda a estrutura do projeto. Vamos construir um pipeline de dados que ingira, processe, armazene e exponha mensagens de um grupo do Telegram para que profissionais de dados possam realizar análises ou até mesmo você. A arquitetura proposta é dividida em duas etapas: transacional, no Telegram, onde os dados são produzidos, e analítica, na Amazon Web Services (AWS), onde os dados são analisados.

Dentro dessa estrutura, uma atividade analítica de interesse é a de realizar a análise exploratória de dados enviadas a um chatbot para responder perguntas como:

Qual o horário que os usuários mais acionam o bot?
Qual o problema ou dúvida mais frequente?
O bot está conseguindo resolver os problemas ou esclarecer as dúvidas?
Etc.
Uma ilustração de como é a estrutura do chatbot:

arquitetura-do-projeto
Telegram
O Telegram representa a fonte de dados transacionais. Mensagens enviadas por usuários em um grupo são capturadas por um bot e redirecionadas via webhook do backend do aplicativo para um endpoint (endereço web que aceita requisições HTTP) exposto pelo AWS API Gateway. As mensagens trafegam no corpo ou payload da requisição.

AWS | Ingestão
Uma requisição HTTP com o conteúdo da mensagem em seu payload é recebia pelo AWS API Gateway que, por sua vez, as redireciona para o AWS Lambda, servindo assim como seu gatilho. Já o AWS Lambda recebe o payload da requisição em seu parâmetro event, salva o conteúdo em um arquivo no formato JSON (original, mesmo que o payload) e o armazena no AWS S3 particionado por dia.

AWS | ETL
Uma vez ao dia, o AWS Event Bridge aciona o AWS Lambda que processa todas as mensagens do dia anterior (atraso de um dia ou D-1), denormaliza o dado semi-estruturado típico de arquivos no formato JSON, salva o conteúdo processado em um arquivo no formato Apache Parquet e o armazena no AWS S3 particionado por dia.

AWS | Apresentação
Por fim, uma tabela do AWS Athena é apontada para o bucket do AWS S3 que armazena o dado processado: denormalizado, particionado e orientado a coluna. Profissionais de dados ou você podem então executar consultas analíticas (agregações, ordenações, etc.) na tabela utilizando o SQL para a extração de insights.
