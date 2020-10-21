# Fluxo da comunicação cliente-servidor
- Cliente envia uma requisição HTTP para o servidor
  - Formato da requisição: ':client_id/:topic/:optional. 
    - :client_id é gerado automaticamente do lado do cliente.
    - :topic é topico alvo, pode ser 'quotes', 'stocks', 'subscriptions' e 'transactions'
    - :optional é 'listen' quando deseja abrir um stream de eventos para o :topic 
- Servidor recebe requisição (GET, PUT ou DELETE)
  - Se for primeiro GET(identificado pela url ':client_id/' , sem :topic) cria o broker para o novo cliente
  - Senão envia o request para o broker do cliente 