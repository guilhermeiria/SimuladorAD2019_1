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

    def servidorIniciaServico(self, tempoAtual, cliente):
        # ToDo nem sempre servico inicia do servidor ocioso
        self.clienteEmAtendimento = cliente
        # ToDo Se servidor jah esta ocupado, nao alterar condicao nem atualizar tempo ocioso
        if not self.ocupado:
            # print "Servidor ocioso. A atender"
            self.ocupado = True
            self.tempoOcioso += (tempoAtual - self.ultimoInstanteOcioso)
            self.ultimoInstanteOcioso = tempoAtual
        # self.tempoDeServicoGerado = tempoAtual + self.agendador.agendarServico()
        # return self.tempoDeServicoGerado

    #def removerClienteServico(self, tempoAtual, cliente):
    def removerClienteServico(self, tempoAtual):
        # print "Servidor. rotina remover cliente somente se fila vazia"
        self.ocupado = False
        self.ultimoInstanteOcioso = tempoAtual
        self.clienteEmAtendimento = None

    def utilizacaoReal(self, tempoAtual):
        if tempoAtual:
            self.tempoSimulacao = tempoAtual
            return (self.tempoSimulacao - self.tempoOcioso) / self.tempoSimulacao
        else:
            return 0.0
