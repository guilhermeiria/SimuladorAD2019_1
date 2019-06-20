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
    
    #ToDo: Tratar evento aqui 
    # Tipo de evento { 0 == Chegada; 1 == Fim de serviço}
    def adicionarEvento (self, tipoDeEvento, Id_cliente, instante):
        # ToDo modificar funcoes do agendamento para ser necessario
        ## somente passar o tipo de evento e a classe decide qual o intervalo 
        ## calcular.
        # Se evento for do tipo chegada
        if not tipoDeEvento:
            proxEvento = Evento( self.tempoAtual + self.agendador.agendarChegada(), Id_cliente, tipoDeEvento)
        else:
            proxEvento = Evento( self.tempoAtual + self.agendador.agendarServico(), Id_cliente, tipoDeEvento)

        self.listaDeEventos.append(proxEvento)
        #Ordenar lista de eventos por instante
        self.listaDeEventos = sorted(self.listaDeEventos, key=lambda evento: evento.tempo)
        
    
    def adicionarClienteNaFila (self, cliente):
        
      
        self.areaClientesFilaEsperaPorIntervalTempo += self.qntClientesFilaDeEspera * (self.tempoAtual - self.instanteUltimoEvento)
        self.instanteUltimoEvento = self.tempoAtual

        #ToDo : Pode se otimizar usando funcoes de lista
        self.qntClientesFilaDeEspera += 1
        self.qntClientesSistema += 1

        #DEBUG
        #print "Add cliente: ", cliente.id

        #Dependendo da disciplina de atendimento em execucao, o cliente 
        # eh adicionado no inicio (FCFS, fila propriamente) ou no 
        # final da fila (LCFS, como uma pilha) 
        if self.disciplinaAtendimentoFCFS:
            #print "FCFS"
            # OTIMIZACAO  Avaliar custo de se adicionar na primeira posicao
            ## Ha estrutura otimizada para "pop left"?
            self.fila.insert(0,cliente)
        else:
            #print "LCFS"
            if self.servidor.ocupado:
                # Se o servidor estiver ocupado, o ultimo elemento deve ser o cliente em atendimento
                # CHECK
                #print "Cliente em atendimento igual a ultimo cliente da fila: "
                #print self.servidor.clienteEmAtendimento.id == self.fila[-1].id
                # Se confirmado, adicionar na penultima posicao
                # OTIMIZACAO Avaliar custo para adicionar na penultima posicao 
                self.fila.insert(-1,cliente)
                #OTIMIZACAO: Inserir return aqui ? Se servidor ocupado,
                # basta adicionar cliente e sair
                # No caso de não haver cliente em atendimento, fila deve ser vazia por se tratar de
                # um sistema conservativo
            else:
                # CHECK
                #print "Sistema Conservativo :"
                #print len(self.fila) == 0
                self.fila.append(cliente)
        # Verifica se o servidor esta ocioso para iniciar servico prontamente.
        if not self.servidor.ocupado:
            #print '\t'," -- Servidor nao ocupado. Cliente entra em servico"
            # A funcao abaixo inicializa o servico do cliente e retorna o tempo de servico gerado 
            ## para o cliente. A variavel sera utilizada para o agendamento do evento de Fim de servico
            #cliente.tempoServico = self.servidor.servidorIniciaServico(self.tempoAtual, cliente)
            # UPDATE: Agora a funcao e chamada somente para inicializar o servico do cliente no servidor.
            # O agendamento eh feito na funcao de gerar eventos.
            self.servidor.servidorIniciaServico(self.tempoAtual, cliente)
            self.qntClientesFilaDeEspera -= 1

            # Tempo na fila de espera deve ser zero pois entrou em 
            ## fila ociosa
            # ToDo verificar se tempo na fila de espera eh realmente zero
            cliente.tempoFilaEspera = self.tempoAtual - cliente.chegada
            #print '\t'," -- tempo na fila de espera = ",cliente.tempoFilaEspera

            #soma a variavel acumulando o total de tempo de espera
            #na fila de espera
            # Acumulo de tempo de espera para calculo simples de media
            self.somaTempoFilaEspera += cliente.tempoFilaEspera
            # Adcionar valor chamando funcao da classe calculadora 
            self.calculadoraAmostraWq.adicionaValor(cliente.tempoFilaEspera)


            # Cliente sera atendido, gerar tempo de servico e adicionar evento fim de servico
            
            #print '\t'," -- servico agendado = ", cliente.tempoServico, "cliente: ", cliente.id
            
            # Criar evento de fim de servico. Tipo de evento == 1
            self.adicionarEvento(1, cliente.id, cliente.tempoServico)
            #proxEventoFimdeServ = Evento(cliente.tempoServico, cliente.id, 1)
            # Adicionar na lista de eventos
            ## ToDo: comparar instante com proxChegada
            #self.listaDeEventos.append(proxEventoFimdeServ)

            #print '\t'," -- Tam lista eventos", len(self.listaDeEventos)
        # Nao ha nada a mais para ser feito no caso do servidor ocupado. 
        '''
        else:
            #print '\t'," -- Servidor Ocupado"
            #print '\t'," -- Mostrar Fila : "
            for i in self.fila:
                print i.id, i.chegada, i.tempoServico
        print '\t'," - agendando prox chegada"
        '''
        
        # agendar proximo evento de chegada
        ## MODIFICADO: tarefa de agendar nova chegada fica para o loop principal
        #self.clienteID += 1
        
        #proxChegadaEvento = Evento(self.tempoAtual + self.agendador.agendarChegada(), self.clienteID, 0)
        #self.listaDeEventos.append(proxChegadaEvento)
        #print '\t'," - Prox chegada em: ", proxChegadaEvento.tempo, " Cliente : ",proxChegadaEvento.refCliente
        
        #print '\t'," - antes de ordenar. Tam = ", len(self.listaDeEventos)
        #for x in self.listaDeEventos :
        #    print x.tempo, x.refCliente, x.tipo, "\n"
        # O tempo de servico gerado sera comparado com todos os eventos que forem agendado ate ele ser 
        ## executado. Portanto toda a lista de eventos deve ser ordenada
        
        # a lista de eventos eh de fato ordenada aqui
        #self.listaDeEventos = sorted(self.listaDeEventos, key=lambda evento: evento.tempo)
        
        #print "ordenar lista eventos por tempo"

        #print "depois"
        #for x in self.listaDeEventos :
        #    print x.tempo, x.refCliente, x.tipo, "\n"

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
            #Pegar referencia de prox. Cliente. Ultimo elemento da fila
            proxClienteServico = self.fila[-1]
            #print '\t'," --- Fila com cliente a atender. Prox Cliente: ", proxClienteServico.id 
            # Inserir cliente em servico e adicionar tempo
            # de servico gerado 
            #proxClienteServico.tempoServico = self.servidor.servidorIniciaServico(self.tempoAtual, proxClienteServico)
            
            # UPDATE: Agora a funcao e chamada somente para inicializar o servico do cliente no servidor.
            # O agendamento eh feito na funcao de gerar eventos.
            self.servidor.servidorIniciaServico(self.tempoAtual, proxClienteServico)
            # Atualizar tempo em fila de espera do cliente
            proxClienteServico.tempoFilaEspera = self.tempoAtual - proxClienteServico.chegada
            

            self.areaClientesFilaEsperaPorIntervalTempo += self.qntClientesFilaDeEspera * (self.tempoAtual - self.instanteUltimoEvento)
            self.instanteUltimoEvento = self.tempoAtual

            self.qntClientesFilaDeEspera -= 1

            #print '\t'," --- tempo na fila de espera = ",proxClienteServico.tempoFilaEspera

            #soma a variavel acumulando o total de tempo de espera
            #na fila de espera
            self.somaTempoFilaEspera += proxClienteServico.tempoFilaEspera

            self.calculadoraAmostraWq.adicionaValor(proxClienteServico.tempoFilaEspera)

            # Adicionar evento de fim de servico
            self.adicionarEvento(1, proxClienteServico.id, proxClienteServico.tempoServico)

            # Cliente sera atendido, gerar tempo de servico e add evento fim de serv
            
            #print '\t'," --- servico agendado = ", proxClienteServico.tempoServico, "cliente: ", proxClienteServico.id
            
            # Criar evento de fim de servico
            #proxEventoFimdeServ = Evento(proxClienteServico.tempoServico, proxClienteServico.id, 1)
            # Adicionar na lista de eventos
            ## ToDo: comparar instante com proxChegada
            #self.listaDeEventos.append(proxEventoFimdeServ)

            #print '\t'," - antes de ordenar. Tam = ", len(self.listaDeEventos)
            #for x in self.listaDeEventos :
                #print x.tempo, x.refCliente, x.tipo, "\n"
            # O tempo de servico gerado sera comparado com todos os eventos que forem agendado ate ele ser 
            ## executado. Portanto toda a lista de eventos deve ser ordenada
            
            # Definicao da funcao que fornecera a chave desejada (o instante agendado) para criterio de
            ## ordenamento
            #self.listaDeEventos = sorted(self.listaDeEventos, key=lambda evento: evento.tempo)
            
            #print "ordenar lista eventos por tempo"

            #print "depois"
            #for x in self.listaDeEventos :
            #    print x.tempo, x.refCliente, x.tipo, "\n"
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
        print inicioSim 
        '''
        print "Ver.: 0.4.2"
        print "M/M/1: ", not self.modoDeExec
        print "Mu: ", self.mu
        print "Lambda: ", self.lambd
        print "FCFS: ", self.disciplinaAtendimentoFCFS
        '''

        #ToDo: Por enquanto o criterio de parada eh a qnt de clientes
        criterioParada = False

        # ToDo: Placement da variavel tempo atual
            # Movendo var. tempoAtual para a simulacao

        # qntRodadas sera 3200 com incrementos de 100 em casos especificos... a ver
        qntClientesRodada = 50000

        # ToDo: Definir criterio de parada da Simulacao
        while not criterioParada:
            #print "Tam lista eventos - inc crit parada", len(self.listaDeEventos)
            
            # Enquanto  nao  parar simulacao, executar prox. evento
            #print tempoAtual + self.agendador.agendarChegada(self.lambd[0])
            # Verifica se lista de eventos contém qualquer elemento 
            # (se lista vazia, self.listaDeEventos == False)
            if self.listaDeEventos:
                #print '\n\t',"Tratar Evento"
                
                # Tratar Evento
                eventoAtual = self.listaDeEventos.pop(0)
                self.tempoAtual = eventoAtual.tempo

                #print '\t',"Tempo Atual", self.tempoAtual, "ID cliente ", eventoAtual.refCliente
                #print " tipo", eventoAtual.tipo

                # Checar tipo de evento 
                # {0 == Chegada; 1 == Fim de servico}
                ## Se evento é tipo chegada
                if not eventoAtual.tipo:
                # Func Adicionar cliente na fila. 
                    #print '\t'," - evento tipo chegada"

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
                    #print '\t'," - Tratar evento fim de servico"
                    # CHECK: consistencia: cliente em atendimento é o mesmo 
                    # referenciado no evento ?
                    #print '\t'," - user em atendimento consistente com evento FimdServ? " 
                    #print self.servidor.clienteEmAtendimento.id == eventoAtual.refCliente
                    # Remover cliente da fila de atendimento
                    self.removerClienteDaFila(self.servidor.clienteEmAtendimento)
                    #agendar outra chegada no proximo loop principal
            # Lista Vazia, agendar chegada
            else:
                #print '\n\t',"Lista vazia: agendar chegada"
                #Criar evento chegada (tipo  0)
                ## gerar tempo de chegada // sera uma chamada a funcao correspondente do agendador
                #intervaloChegada = self.agendador.agendarChegada()
                #self.clienteID += 1
                #print '\t'," -chegada gerada: ", intervaloChegada, "Cliente: ", self.clienteID
                #proxEvento = Evento(self.tempoAtual + intervaloChegada, self.clienteID, 0)
                #self.listaDeEventos.append(proxEvento)
                # Se lista vazia, criar evento de chegada
                self.clienteID += 1
                self.adicionarEvento(0, self.clienteID, self.tempoAtual)
            # Printa utilizacao do servidor no momento            
            #print "Utilizacao atual: ", self.servidor.utilizacaoReal(self.tempoAtual)

            # ToDo alterar conforme criterio de parada! checar se criterio de parada    
            if self.qntClientesAtendidos == qntClientesRodada:    
                criterioParada = True
            


        print "tempo de Simulacao: ", datetime.now() - inicioSim
        print "Ver.: 0.4.4"
        print "M/M/1: ", not self.modoDeExec
        print "Mu: ", self.mu
        print "Lambda: ", self.lambd
        print "FCFS: ", self.disciplinaAtendimentoFCFS
        print "Conteudo da fila"
        # Printar conteúdo da fila
        #for i in self.fila:
        #    print i.id, i.chegada, i.tempoServico
        print "Tempo Atual: ", self.tempoAtual
        #print "Soma tempo fila de espera :"
        #print self.somaTempoFilaEspera
        #print "Soma tempo total no sistema :"
        #print self.somaTempoSistema
        #print "Media de Clientes na fila: "

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

if __name__ == '__main__':

    s = Simulacao()
    s.executarSim()
        




        

