# Fluxo da comunicação cliente-servidor
- Cliente envia uma requisição HTTP para o servidor
  - Formato da requisição: ':client_id/:topic/. 
    - :client_id é gerado automaticamente do lado do cliente.
    - :topic é topico alvo, pode ser 'quotes', 'subscriptions', 'listen', 'stocks' e 'order'
- Servidor recebe requisição (GET, PUT ou DELETE)
  - Se for primeiro GET(identificado pela url ':client_id/' , sem :topic) cria o controller para o novo cliente
  - Senão envia o request para o controller do cliente 
  - Se for um request interno (identificado pela url '/brokers/') direciona request para o 'servidor' simulado de brokers
