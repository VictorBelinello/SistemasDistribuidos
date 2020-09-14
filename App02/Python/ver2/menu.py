import os

class Menu:
  """String usada para finalizar/separar um menu, para melhor visualização"""
  SEPARATOR = "*"*30
  HEADLINE_WIDTH = 30

  def __init__(self, master):
    self.master = master

  """Obtém uma opção de menu do usuário e converte de acordo com o argumento cast."""
  @staticmethod
  def getNumericInput(cast=int, input_message="Opção: "):
      opt = input(input_message)
      try:
        opt = cast(opt)
        return opt
      except ValueError as e:
        print("Erro convertendo '{0}' para {1}".format(opt, cast))
        input("Pressione ENTER.")
      finally:
        # Limpa o terminal de acordo com o SO
        os.system('cls' if os.name == 'nt' else 'clear')


  """Procura uma empresa pelo nome fornecido pelo usuário e retorna o objeto Company equivalente, se não encontrar retorna None"""
  def getCompanyInput(self):
    company_name = input("Informe nome da empresa: ").upper()
    return self.master.getCompanyIfExists(company_name)
      

  """Função chamada ao acessar opção 1 do menu principal"""
  def optionQuotes(self, redirect=False ):
    print("MENU COTAÇÕES".center(Menu.HEADLINE_WIDTH))
    print("Digite 1 para mostrar sua lista cotações")
    print("Digite 2 para adicionar uma empresa")
    print("Digite 3 para remover uma empresa")
    print("Digite 0 para voltar ao menu principal")
    print(Menu.SEPARATOR)

    opt = Menu.getNumericInput( )
    
    
    if opt == 1:
      string = "Lista cotações vazia." if not self.master.getQuotes() else "".join(self.master.getQuotes())
      print(string)
      print(Menu.SEPARATOR)
      input("ENTER para prosseguir.")
    elif opt == 2 or opt == 3:
      company = self.getCompanyInput()
      if company:
        pass
      print(Menu.SEPARATOR)
      input("ENTER para prosseguir.")

  """Função chamada ao acessar opção 2 do menu principal"""
  def optionStocks(self ):
    print("MENU AÇÕES".center(Menu.HEADLINE_WIDTH))
    print("Digite 1 para mostrar suas ações")
    print("Digite 2 para comprar uma ação")
    print("Digite 3 para vender uma ação")
    print("Digite 0 para voltar ao menu principal")
    print(Menu.SEPARATOR)

    opt = Menu.getNumericInput( )

    if opt == 1:
      print("NOT IMPLEMENTED YET")
      raise NotImplementedError
    elif opt == 2 or opt == 3:
      company = self.getCompanyInput()
      if company:
        pass
      print(Menu.SEPARATOR)
      input("ENTER para prosseguir.")


  """Função chamada ao acessar opção 3 do menu principal"""
  def optionNotifications(self ):
    print("MENU NOTIFICAÇÕES".center(Menu.HEADLINE_WIDTH))
    print("Digite 1 para ver sua lista de notificações")
    print("Digite 2 para adicionar uma notificação")
    print("Digite 0 para voltar ao menu principal")
    print(Menu.SEPARATOR)

    opt = Menu.getNumericInput( )

    if opt == 1:
      print("NOT IMPLEMENTED YET")
      raise NotImplementedError
    elif opt == 2:
      company = self.getCompanyInput()
      if company:
        pass
      print(Menu.SEPARATOR)
      input("ENTER para prosseguir.")

  def showMainMenu(self ):
    while True:
      # Limpa o terminal de acordo com o SO
      os.system('cls' if os.name == 'nt' else 'clear')
      print("MENU PRINCIPAL".center(Menu.HEADLINE_WIDTH))
      print("Digite 1 para gerir lista cotações")
      print("Digite 2 para gerir suas ações")
      print("Digite 3 para gerir alertas")
      print("Digite 0 para sair")
      print(Menu.SEPARATOR)

      opt = Menu.getNumericInput()

      if opt == 1:
        self.optionQuotes()
      elif opt == 2:
        self.optionStocks()
      elif opt == 3:
        self.optionNotifications()
      elif opt == 0:
        break

      