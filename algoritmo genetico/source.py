import copy, random, requests, string
from datetime import datetime

# Parametrizações do algoritmo genético
QtdGeracoes = 42 # Default = [42]
QtdIndividuos = 100 # Default = [100]
QtdItensElitismo = 10 # Quantidade de indivíduos com a melhor nota que serão levados para a próxima geração / Default = [10]
QtdCaracteresMutacao = 3 # Default = [3]
TaxaCorteCruzamento = 86 # Default = [86] - 60%

# Parametrizações do simulador
QtdSemaforos = 24 # Default = [24]
TamanhoCromossomo = QtdSemaforos * 6 # Default = [QtdSemaforos * 6]
TempoExecucaoSimulador = 30 # Default = [30]
Url = 'http://localhost:53986/avaliar' # Default = [http://localhost:53986/avaliar]

# Variáveis de controle
Individuo = [0 for x in range(QtdIndividuos)]
ListaDePais = [0 for x in range(QtdIndividuos)] # Lista de itens que serão pais na próxima geração
Nota = [0 for x in range(QtdIndividuos)]

def main():
	IniciaPopulacao()
	Avalia()

	for X in range(QtdGeracoes):
		ImprimeGeracao(X)
		Elitismo()
		Cruzamento()
		Mutacao()
		VerificaSinaisCompletamenteParados()
		Copia()
		Avalia()

def IniciaPopulacao(): # Método responsável por inicializar a população da 1ª geração do algoritmo genético
	for X in range(QtdIndividuos):
		for Y in range(QtdSemaforos): # Para cada semáforo é montado uma string de 6 caracteres que informa o acionamento do semáforo em intervalos de 10 segundos
			if (Y == 0):
				Individuo[X] = '{:0>6}'.format(int(str(bin(random.randint(1, 62))).replace('0b', ''))); # Ex: 010011 (dentro de um intervalo de 60 segundos, o semáforo ligará por 10 segundos e depois por mais 20)
			else:
				Individuo[X] = str(Individuo[X]) + '{:0>6}'.format(int(str(bin(random.randint(1, 62))).replace('0b', '')));

def Avalia():
	for X in range(QtdIndividuos):
		response = requests.post(Url, json = { "cromossomo" : Individuo[X], "tempoExecucaoSimulador" : TempoExecucaoSimulador }) # Passa cada cromossomo da lista de indivíduos da geração em execução para avaliar
		Nota[X] = float(response.text) # A nota em questão é a soma do tempo médio de viagem em segundos de todas as rotas possíveis

def ImprimeGeracao(Geracao): # Cria um arquivo com o registro de todos os indivíduos de cada geração
	file = open('Geracao' + str(Geracao + 1) + '.txt', 'w+')

	file.write('Geração ' + str(Geracao + 1) + ' - ' + str(datetime.now()) + '\r\n\r\n')

	for X in range(QtdIndividuos):
		file.write(Individuo[X] + ' - Nota: ' + str(Nota[X]) + '\r\n')

	file.close()

def Elitismo():
	NotasOrdenadas = sorted((e, i) for i, e in enumerate(Nota)) # Cria um novo array com as notas ordenadas e com os índices originais (para poder encontrar o indivíduo que representa esta nota)

	for X in range(QtdItensElitismo):
		ListaDePais[X] = copy.copy(Individuo[NotasOrdenadas[X][1]]) # Faz uma cópia dos melhores indivíduos para a lista da próxima geração

def Cruzamento():
	for X in range(QtdItensElitismo, QtdIndividuos): # Retorna todos os índices restantes a serem preenchidos com cruzamento
		A = 0
		B = 0

		while(A == B):
			A = random.randint(0, QtdItensElitismo - 1);
			B = random.randint(0, QtdItensElitismo - 1);

		ListaDePais[X] = ListaDePais[A][:TaxaCorteCruzamento] + ListaDePais[B][TaxaCorteCruzamento:] # Pega N caracteres de A e junta com N caracteres de B

def Mutacao():
	for X in range(QtdItensElitismo, QtdIndividuos): # Faz a mutação apenas dos itens cruzados
		for Y in range(QtdCaracteresMutacao):
			A = random.randint(0, TamanhoCromossomo - 1)

			Novo = ''

			for O in range(0, A): # Percorre os caracteres até a posição que sofrerá mutação
				Novo += ListaDePais[X][O]

			# Faz a mutação do caracter em uma posição aleatória do cromossomo
			if ListaDePais[X][A] == '0':
				Novo += '1'
			else:
				Novo += '0'

			for L in range(A + 1, TamanhoCromossomo): # Percorre o restante de caracteres do cromossomo
				Novo += ListaDePais[X][L]

			ListaDePais[X] = Novo

def VerificaSinaisCompletamenteParados():
	for X in range(QtdIndividuos):
		for Y in range(QtdSemaforos): # Para cada semáforo do indivíduo
			I = Y * 6 # Índice de início do semáforo dentro do cromossomo
			if ListaDePais[X][I:][:6] == '000000': # Ajuste feito para evitar que um semáforo fique completamente parado
				Novo = ''

				for O in range(0, I): # Percorre os caracteres até a posição do semáforo que está completamente parado
					Novo += ListaDePais[X][O]
				for K in range(6): # Inverte a configuração do semáforo em questão deixando-o completamente ativo
					Novo += '1'
				for L in range(I + 6, TamanhoCromossomo): # Percorre o restante de caracteres do cromossomo
					Novo += ListaDePais[X][L]

				ListaDePais[X] = Novo

def Copia(): # Atribui ao array de indivíduos a lista completa de itens da próxima geração
	for X in range(QtdIndividuos):
		Individuo[X] = copy.copy(ListaDePais[X])

main() # Faz a chamada do método principal que inicializa o algoritmo