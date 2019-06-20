#!/usr/bin/env python2.7
# coding=UTF8

from Calculadora import Calculadora
import random
from datetime import datetime

class Simulacao(object):
    def __init__(self):
        # Media da taxa de servico. Default deve ser 1.0       
        self.mu = 1.0
        # Lista com os valores exigidos de utilização para a simulação 
        # # + super utilizacao para testes de formacao de fila
        self.rhoValores = [0.2, 0.4, 0.6, 0.8, 0.9, 1.1]

        # Deve-se selecionar um dos valores disponiveis na lista para o rho.
        # Valor Padrao e 0.2
        self.rho = self.rhoValores[1]

        # Por padrao a disciplina de atendimento é a FCFS, caso queira-se a LCFS, mudar para False
        self.disciplinaAtendimentoFCFS = True

        # Calcula Taxa de entrada conforme a utilização desejada. 
        # # No caso de depuracao, alterar diretamente.
        self.lambd = self.rho * self.mu

        self.tempoAtual = 0.0

        self.clienteID = 0
        self.listaDeEventos = []
        self.qntDeRodadas = 100
        self.rodadaAtual = 0

        # Alfa utilizado para o intervalo de confianca
        alpha = 0.95

        #Tipo de Execucao {0 = fila M/M/1; 1 = modo de depuracao
        # (fila D/D/1) }
        self.modoDeExec = 0

        self.agendador = Agendador(self.modoDeExec, self.lambd, self.mu)

        # Estrutura da Fila
        self.fila = []
        # variaveis da fila
        self.qntClientesFilaDeEspera = 0
        self.qntClientesSistema = 0
        self.somaTempoFilaEspera = 0.0
        self.somaTempoSistema = 0.0
        self.qntClientesAtendidos = 0
        self.areaClientesFilaEsperaPorIntervalTempo = 0.0
        self.instanteUltimoEvento = 0.0
        #self.servidorOcupado = False

        self.servidor = Servidor(self.mu, self.rho, self.agendador)

        # Instancias de calculadoras para o tempo na fila de espera
        self.calculadoraAmostraWq = Calculadora(alpha)
        self.calculadoraRodadasWq = Calculadora(alpha)
     
    # Tipo de evento { 0 == Chegada; 1 == Fim de serviço}
    def adicionarEvento (self, tipoDeEvento, Id_cliente, instante):
        # Se evento for do tipo chegada
        if not tipoDeEvento:
            proxEvento = Evento( self.tempoAtual + self.agendador.agendarChegada(), Id_cliente, tipoDeEvento)
        else:
            proxEvento = Evento( self.tempoAtual + self.agendador.agendarServico(), Id_cliente, tipoDeEvento)

        self.listaDeEventos.append(proxEvento)
        #Ordenar lista de eventos por instante de ocorrencia do evento (campo tempo)
        self.listaDeEventos = sorted(self.listaDeEventos, key=lambda evento: evento.tempo)
        
    
    def adicionarClienteNaFila (self, cliente):
        self.areaClientesFilaEsperaPorIntervalTempo += self.qntClientesFilaDeEspera * (self.tempoAtual - self.instanteUltimoEvento)
        self.instanteUltimoEvento = self.tempoAtual

        self.qntClientesFilaDeEspera += 1
        self.qntClientesSistema += 1

        #Dependendo da disciplina de atendimento em execucao, o cliente 
        # eh adicionado no inicio (FCFS, fila propriamente) ou no 
        # final da fila (LCFS, como uma pilha) 
        if self.disciplinaAtendimentoFCFS:
            # FCFS. Adicionando cliente no 
            self.fila.insert(0,cliente)
        else:
            if self.servidor.ocupado:
                # Se o servidor estiver ocupado, o ultimo elemento deve ser o cliente em atendimento
                # Portanto adicionar cliente na penultima posicao
                self.fila.insert(-1,cliente)
            else:
                # Se nao ha cliente em atendimento, logo fila esta vazia
                # Adicionar cliente na ultima posicao (append)
                self.fila.append(cliente)
        # Verifica se o servidor esta ocioso para iniciar servico prontamente.
        if not self.servidor.ocupado:
            # Inicia atendimento do cliente pelo servidor
            self.servidor.servidorIniciaServico(self.tempoAtual, cliente)
            self.qntClientesFilaDeEspera -= 1

            # Tempo na fila de espera deve ser zero pois entrou em 
            ## fila ociosa.
            cliente.tempoFilaEspera = self.tempoAtual - cliente.chegada

            #soma a variavel acumulando o total de tempo de espera
            #na fila de espera
            # Acumulo de tempo de espera para calculo simples de media
            self.somaTempoFilaEspera += cliente.tempoFilaEspera
            
            # VERIFICAR SE REALMENTE NECESSARIO
            # Adicionar valor chamando funcao da classe calculadora 
            self.calculadoraAmostraWq.adicionaValor(cliente.tempoFilaEspera)

            # Criar evento de fim de servico. Tipo de evento == 1
            self.adicionarEvento(1, cliente.id, cliente.tempoServico)


    def removerClienteDaFila(self, cliente):
        # CHECK se cliente no pop eh o msm em atendimento. DONE
        #print '\t'," - Removendo Cliente" 
        # decrementa qnt de clientes no sistema
        self.qntClientesSistema -= 1
        #CHECK. Cliente sendo liberado eh o mesmo do referenciado
        ## por essa chamada de funcao ?
            #print '\t'," -- Check: Cliente saindo igual ao cliente em referencia?"
            #print "Ultimo fila", self.fila[-1].id
        clienteSaindo = self.fila.pop()

        # ToDo: Try...catch CHECK se cliente saindo id == ultimo cliente na fila id
        #print "sai cliente: ", clienteSaindo.id 
            #print "cliente no serv: ",cliente.id

            #print '\t'," -- Check N == variavel de controle de clientes na fila ?"
            #print len(self.fila) == self.qntClientesSistema

        # Atualiza tempo em sistema do cliente
        cliente.tempoSistema = self.tempoAtual - cliente.chegada

        # CHECK

        self.somaTempoSistema += cliente.tempoSistema

        self.qntClientesAtendidos += 1

        # Verificar se ha prox Cliente na fila
        ## so eh necessario liberar o serv. se nao houver outro cliente.
        ## se tiver cliente em espera, basta chamar inserirClienteServ mudando o cliente
        ## Com isso o servidor não recalcula o tempo ocioso
        if len(self.fila):
            #Pegar referencia de prox. Cliente a ser atendido que eh o Ultimo elemento da fila
            proxClienteServico = self.fila[-1]

            self.servidor.servidorIniciaServico(self.tempoAtual, proxClienteServico)
            
            # Atualizar tempo em fila de espera do cliente
            proxClienteServico.tempoFilaEspera = self.tempoAtual - proxClienteServico.chegada
            
            # Acumula a area da ultima mudanca para calculo de E[Nq]
            self.areaClientesFilaEsperaPorIntervalTempo += self.qntClientesFilaDeEspera * (self.tempoAtual - self.instanteUltimoEvento)
            # Atualiza instante que ocorreu ultima mudanca de area
            self.instanteUltimoEvento = self.tempoAtual

            self.qntClientesFilaDeEspera -= 1

            #soma a variavel acumulando o total de tempo de espera
            #na fila de espera
            self.somaTempoFilaEspera += proxClienteServico.tempoFilaEspera

            self.calculadoraAmostraWq.adicionaValor(proxClienteServico.tempoFilaEspera)

            # Adicionar evento de fim de servico
            self.adicionarEvento(1, proxClienteServico.id, proxClienteServico.tempoServico)

        else:
            #Se nao houver ninguem na fila a ser atendido, entao
            # chama rotina de liberar servidor
            self.servidor.removerClienteServico(self.tempoAtual, cliente)               
    # Funcoes Estatisticas

    def esperanca_Nq_analitico(self, lambd, mediaW):
        return lambd*mediaW

    def esperanca_W_analitico(self, rho, mu):
        return rho/(mu*(1-rho))


    def executarSim(self):
        inicioSim = datetime.now()

        #ToDo: Por enquanto o criterio de parada eh a qnt de clientes
        criterioParada = False

        # qntRodadas sera 3200 com incrementos de 100 em casos especificos... a ver
        qntClientesRodada = 50000

        # ToDo: Definir criterio de parada da Simulacao
        while not criterioParada:
            # Verifica se lista de eventos contém qualquer elemento 
            # (se lista vazia, self.listaDeEventos == False)
            if self.listaDeEventos:
                # Tratar Evento
                eventoAtual = self.listaDeEventos.pop(0)
                self.tempoAtual = eventoAtual.tempo

                # Checar tipo de evento 
                # {0 == Chegada; 1 == Fim de servico}
                ## Se evento é tipo chegada
                if not eventoAtual.tipo:
                    # Adicionar Cliente na fila de atendimento 
                    ## Instanciar cliente
                    clienteAtual = Cliente(self.tempoAtual, eventoAtual.refCliente)   
                    self.adicionarClienteNaFila(clienteAtual)
                    # Cada chegada desencadeia o agendemento de uma nova
                    self.clienteID += 1
                    self.adicionarEvento(0, self.clienteID, self.tempoAtual)
                   
                # Senao, entoa se trata de um evento Fim de servico 
                # tipo de evento == 1    
                else:
                    # Remover cliente da fila de atendimento
                    self.removerClienteDaFila(self.servidor.clienteEmAtendimento)
            
            # Lista de eventos Vazia, agendar chegada
            else:
                # Se lista vazia, criar evento de chegada (evento tipo 0). 
                self.clienteID += 1
                self.adicionarEvento(0, self.clienteID, self.tempoAtual)
            # Printa utilizacao do servidor no momento            
            #print "Utilizacao atual: ", self.servidor.utilizacaoReal(self.tempoAtual)

            # ToDo alterar conforme criterio de parada! checar se criterio de parada    
            if self.qntClientesAtendidos == qntClientesRodada:    
                criterioParada = True
            


        print "tempo de Simulacao: ", datetime.now() - inicioSim
        print "Ver.: 0.4.5"
        print "M/M/1: ", not self.modoDeExec
        print "Mu: ", self.mu
        print "Lambda: ", self.lambd
        print "FCFS: ", self.disciplinaAtendimentoFCFS
        print "Conteudo da fila"
        print "Tempo Atual: ", self.tempoAtual
        print "Total de Clientes atendidos: ", self.qntClientesAtendidos
        print "E[W]analitico = ", self.rho/(self.mu*(1-self.rho))
        print "E[W]analtico rho estimado = ", self.esperanca_W_analitico(self.servidor.utilizacaoReal(self.tempoAtual), self.mu)
        print "E[W] simples: ", self.somaTempoFilaEspera/self.qntClientesAtendidos
        print "E[W] pela Calculadora: ", self.calculadoraAmostraWq.get_media()
        print "E[W] pela area calculada: ", self.areaClientesFilaEsperaPorIntervalTempo/self.qntClientesAtendidos
        print "V(W) pela Calculadora: ", self.calculadoraAmostraWq.get_variancia()
        print
        print "Media de Clientes na Fila de Espera: ", self.areaClientesFilaEsperaPorIntervalTempo/self.tempoAtual
        print "Media de Clientes na Fila de Espera analit. Teorico: ", self.lambd*(self.rho/(self.mu*(1-self.rho)))
        print "Media de Clientes na Fila de Espera analit. Dados simulacao: ",self.esperanca_Nq_analitico(self.lambd,self.calculadoraAmostraWq.get_media())
        print "Utilizacao estimada do Servidor: ", self.servidor.utilizacaoReal(self.tempoAtual)



class Servidor(object):
    def __init__(self, txServico, utilizacao, agendador):
        self.txServico = txServico
        self.rho = utilizacao
        self.clienteEmAtendimento = None
        self.agendador = agendador
        self.ocupado = False
        self.tempoOcioso = 0.0
        self.ultimoInstanteOcioso = 0.0

        # Servidor deve retornar se esta ocupado,
        # funcoes secundarias podem ser: retornar utilizacao
        # instantanea, cliente em atendimento 
    
    def servidorIniciaServico (self, tempoAtual, cliente):
        self.clienteEmAtendimento = cliente
        # ToDo Se servidor jah esta ocupado, nao alterar condicao nem atualizar tempo ocioso
        if not self.ocupado:
            self.ocupado = True
            self.tempoOcioso += (tempoAtual - self.ultimoInstanteOcioso)
            self.ultimoInstanteOcioso = tempoAtual

    def removerClienteServico(self, tempoAtual, cliente):
        self.ocupado = False
        self.ultimoInstanteOcioso = tempoAtual
        self.clienteEmAtendimento = None
    
    def utilizacaoReal(self, tempoAtual):
        if tempoAtual:
            self.tempoSimulacao = tempoAtual
            return (self.tempoSimulacao - self.tempoOcioso) / self.tempoSimulacao
        else:
            return 0.0


class Cliente(object):
    def __init__(self, instanteEntrada, Id):
        self.chegada = instanteEntrada
        self.id = Id
        self.tempoServico = -1
        self.tempoFilaEspera = 0.0
        self.tempoSistema = 0.0


class Evento(object):
    """        """
    def __init__(self, tempo, refCliente, tipo ):
        self.tempo = tempo
        self.refCliente = refCliente
        # tipo de evento {0 = Chegada; 1 = termino servico}
        self.tipo = tipo


class Agendador(object):
    def __init__(self, modo, txChegada, txServico):
        self.testeCorretude = modo
        self.txChegada = txChegada
        self.txServico = txServico
    # Caso o modo de execucao seja o de depuracao, os valores agendados serao deterministicos --
    #  -- utilizando as taxas passadas como valores absolutos para intervalos de chegada e 
    # tempo de serviço. Caso contrario o agendamento chama --
    #  -- a funcao responsavel por gerar numeros aleatorios exponencialmente distribuidos --
    #  -- utilizando os parametros como as medias lambda ou mu  
    def agendarChegada(self):
        if self.testeCorretude :
            return self.txChegada
        return random.expovariate(self.txChegada)
    def agendarServico(self):
        if self.testeCorretude :
            return self.txServico
        return random.expovariate(self.txServico)

                
if __name__ == '__main__':

    s = Simulacao()
    s.executarSim()
        




        

