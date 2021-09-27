from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.country_id as Pais
import time, logging, json, configparser
from datetime import datetime, date, timedelta
from dateutil import tz
import sys

#CODIGO PARA DESATIVAR DEBUG OU logging.ERROR
#logging.disable(level=(logging.DEBUG))


# Credenciais
API = IQ_Option('seu_email', 'password')

# Logar
def Login():
    API.connect()

    while True:
        if API.check_connect() == False:
            print('Erro ao se conectar')
            
            API.connect()
        else:
            print('Conectado com sucesso')
            break
        
        time.sleep(1)
# carrega sua banca na api
def getBalance():    
    # Define a conta de utilização
    conta = 'PRACTICE'#input('\nDigite com qual conta quer entrar "REAL" ou "PRACTICE": ')
    API.change_balance(conta) # PRACTICE / REAL 
    return API.get_balance() 
#CONVERT TIMESTAMP PARA HORA HUMANA
def timestamp_converter(x): # Função para converter timestamp
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))
	
	return str(hora)[:-6]   
#PEGA O PERFIL
def perfil():
    return json.loads(json.dumps(API.get_profile_ansyc()))   
#PEGA A BANCA
def banca():
    return json.loads(json.dumps(getBalance()))
#PEGA TOP 10 TRADERS DO MUNDO
def topTrades():
    pais='Worldwide'#"BR"
    da_posicao=1
    para_posicao=30
    traders_perto=0
    return json.loads(json.dumps(API.get_leader_board(pais, da_posicao, para_posicao, traders_perto)))
#PEGA PARIDADES ABERTAS
def payout(par, tipo, timeframe = 1):
	if tipo == 'turbo':
		a = API.get_all_profit()
		return int(100 * a[par]['turbo'])
		
	elif tipo == 'digital':
	
		API.subscribe_strike_list(par, timeframe)
		while True:
			d = API.get_digital_current_profit(par, timeframe)
			if d != False:
				d = int(d)
				break
			time.sleep(1)
		API.unsubscribe_strike_list(par, timeframe)
		return d

def getCandles(par):
    API.start_candles_stream(par, 60, 1)
    time.sleep(1)
    
    vela = API.get_realtime_candles(par, 60)
    
    while True:
        for velas in vela:
            print(vela[velas]['close'])
        time.sleep(1)
    API.stop_candles_stream(par, 60)
   
def configuracao():
    arquivo = configparser.RawConfigParser()
    arquivo.read('config.txt')
    
    return { 'paridade': arquivo.get('GERAL', 'paridade'), 'valor_entrada': arquivo.get('GERAL', 'entrada'), 'timeframe': arquivo.get('GERAL', 'timeframe')}
    
def sinais():
    file = open('sinais.txt', encoding='UTF-8')
    lista = file.read()
    file.close
    
    lista = lista.split('\n')
    
    for index,a in enumerate(lista):
        if a == '':
            del lista[index]
    
    return lista


Login()
print('\n - Inicializando o bot - \n')

# loop infinito para pegar acompanhar velas
# print('\n - Acompanhar velas - \n')
# par = 'EURUSD'
# getCandles(par)

# print meu perfil
data = perfil()
print('\n - Meu perfil - \n')
print(' Apelido: ',data['nickname'])
print(' Email: ',data['email'])
print(' Nome : ',data['name'])
print(' Banca : ', banca())
print(' Criado : ',timestamp_converter(data['created']))

print('\n - Pegando Top Traders - \n')

traders = topTrades()
for colocacao in traders['result']['positional']:
    nome_ranking = traders['result']['positional'][colocacao]['user_name']
    segunda_busca = API.get_user_profile_client(traders['result']['positional'][colocacao]['user_id'])
    print(' Nome:',nome_ranking)
    print(' User ID:',traders['result']['positional'][colocacao]['user_id'])
    print(' Se registrou em:',timestamp_converter(segunda_busca['registration_time']))
    print(' Pais: '+traders['result']['positional'][colocacao]['flag'])
    print(' Faturamento esta semana:',round(traders['result']['positional'][colocacao]['score'], 2))
    print('\n')
    
print(' - Trader(s) Online - \n')

for index in traders['result']['positional']:
    # Pega o user_id do top 10 traders
    id = traders['result']['positional'][index]['user_id']
    # Quarda o perfil de cada trader
    perfil_trader = API.get_user_profile_client(id)
    # Verifica quem está online
    if perfil_trader['status'] == 'online':
        trade = API.get_users_availability(id)
        
        try:       
            tipo = trade['statuses'][0]['selected_instrument_type']
            par = API.get_name_by_activeId(trade['statuses'][0]['selected_asset_id']).replace('/', '')
            
            print('\n [',index,'] ',perfil_trader['user_name'])
            print(' Opção: ',tipo)
            print(' Pariedade: ',par)
        except:
            pass

# print('\n - Pegando pariedades abertas - \n')

# par = API.get_all_open_time()

# for paridade in par['turbo']:
	# if par['turbo'][paridade]['open'] == True:
		# print('[ TURBO ]: '+paridade+' | Payout: '+str(payout(paridade, 'turbo')))
		
# print('\n')

# for paridade in par['digital']:
	# if par['digital'][paridade]['open'] == True:
		# print('[ DIGITAL ]: '+paridade+' | Payout: '+str( payout(paridade, 'digital') ))


# #PEGA OS SINAIS
# print('\n')
# print(json.dumps(sinais(), indent=1))
# lista_sinais = sinais()
# print('\n Quantidade de sinais: ',len(lista_sinais))

# for index, sinal in enumerate(lista_sinais):
    # dados = sinal.split(';')
    
    # while index <= len(lista_sinais):

        # HORA_ATUAL = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        
        # if HORA_ATUAL == dados[0]:
            # print('\n - Abrir ordem opções digitais - \n')
            # pareMoeda = dados[2]
            # entradas = 100.00
            # direcoes = dados[3]#call pra cima put pra baixo
            # timesframe = 1#1minuto;5minutos;15minutos

            # status,id = API.buy_digital_spot(pareMoeda, entradas, direcoes, timesframe)

            # if status:
                # print(' Ordem aberta com sucesso')
                # break
            # else:
                # print(' Não executou a ordem!')
                # break

#PEGA AS CONFIGURAÇÕES
# print('\n\n')
# conf = configuracao()
# print(conf['paridade'])
 
print('\n - Seguir traders - \n')      
# # name:
# # "live-deal-binary-option-placed"
# # "live-deal-digital-option"
while_run_time=10
name="live-deal-digital-option"
active="EURAUD"
_type="PT1M" #"PT1M"/"PT5M"/"PT15M"
buffersize=10
print("_____________subscribe_live_deal_______________")
API.subscribe_live_deal(name,active,_type,buffersize)

start_t=time.time()
while True:
    trades = API.get_live_deal(name,active,_type)
    print("__For_digital_option__ data size:"+str(len(trades)))
    print(trades)
    print("\n\n")
    time.sleep(1)
    # if time.time()-start_t>while_run_time:
        # break
    if len(trades) > 0:
        print(json.dumps(trades[0], indent=1))
print("_____________unscribe_live_deal_______________")
API.unscribe_live_deal(name,active,_type)

# Abrir ordem iq option opções digitais
# print('\n - Abrir ordem opções digitais - \n')

# pareMoeda = 'EURCAD'
# entradas = 100.00
# direcoes = 'call'#call pra cima put pra baixo
# timesframe = 1#1minuto;5minutos;15minutos

# status,id = API.buy_digital_spot(pareMoeda, entradas, direcoes, timesframe)

# if status:
    # print(' Ordem aberta com sucesso')
    # print(' Aguarde a ordem ser concluida')
# else:
    # print(' Não executou a ordem!')
    # sys.exit()

# if isinstance(id, int):
    #while True:
        # resultado,lucro = API.check_win_digital_v2(id)
        
        # if resultado:
            # if lucro > 0:
                # print(' RESULTADO: WIN / LUCRO: '+str(round(lucro,2)))
            # else:
                # print(' RESULTADO: LOSS / PERDA: '+str(entradas))
            # break
#força a saida
#sys.exit()

# Abrir ordem iq option opções binarias
# print('\n - Abrir ordem opções binarias - \n')

# parMoeda = 'AUDCAD-OTC'
# entrada = 100.00
# direcao = 'call'#call pra cima put pra baixo
# timeframe = 1

# status,id = API.buy(entrada, parMoeda, direcao, timeframe)

# if status:
    # resultado,lucro = API.check_win_v3(id)
    # print('RESULTADO: '+resultado+' / LUCRO: '+str(round(lucro, 2)))
    # #Exemplo para pegar resultado
    # # print(API.check_win_v3(id))
    # # print('\n')
    # # print(API.check_win_v4(id))
 
print('\n - Fim das operações - \n')
