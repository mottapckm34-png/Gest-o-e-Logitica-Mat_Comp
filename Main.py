from Cliente import Cliente
from Deposito import Deposito
from AtributosDoNavio import AtributosDoNavio
from BancoDeDados import BancoDeDados

#Imput das Funçoes

def cadastroCliente():
    """ Lê os dados de um Cliente"""   
    print(f"\n Cliente #{proximo_id}")
    nome = input("Nome: ")
    latitude = float(input("Latitude: "))
    longitude = float(input("Longitude: "))
    peso = float(input("Peso da entrega (Kg): "))
    janela_inicio = float(input("Janela de início (Ex: 8.0 = 8:00): "))
    janela_fim = float(input("Janela de fim (Ex: 18.0 = 18:00): "))

    return Cliente(proximo_id,
        nome,
        latitude,
        longitude,
        peso,
        janela_inicio,
        janela_fim
    ) 
    

def cadastroDeposito(): -> Deposito:
   
    """ Lê os dados de um Depósito"""   
    print(f"\n Depósito #{proximo_id}")
    nome = input("Nome: ")
    latitude = float(input("Latitude: "))
    longitude = float(input("Longitude: "))

    return Deposito(proximo_id,
        nome,
        latitude,
        longitude
    )
    

def cadastroAtributosNavio(): -> AtributosDoNavio:
    """ Lê os dados de um Navio"""   
    print(f"\n Navio #{proximo_id}")
    nome = input("Nome: ")
    capacidade = float(input("Capacidade (Kg): "))
    velocidade = float(input("Velocidade (Km/h): "))
    custo_operacional = float(input("Custo operacional (R$/h): "))

    return AtributosDoNavio(proximo_id,
        nome,
        capacidade,
        velocidade,
        custo_operacional
    )
    

def loop_cadastro_clientes(banco: BancoDeDados):
    """ Loop para cadastro de Clientes"""   
print("Cadastro de Clientes ")   

    while True:
        cliente = cadastroCliente()
        banco.clientes.append(cliente)
        print(f"Cliente #{cliente.id} cadastrado com sucesso!")
        continuar = input("Deseja cadastrar outro cliente? (s/n): ")
        if continuar.lower() != 's':
            break

def main():
    

    deposito = cadastroDeposito()
    navio = cadastroAtributosNavio()
    banco = BancoDeDados(Deposito=deposito, Navio=navio)
    loop_cadastro_clientes(banco)
    print("\nCadastro concluído!")


    print(f"Depósito: {banco.deposito}") #mostrar os dados do depósito
    print(f"Navio: {banco.navio}") #mostrar os dados do navio
    print("Clientes cadastrados:") #mostrar os dados dos clientes cadastrados

if __name__ == "__main__": #Ponto de entrada do programa
    main()    
