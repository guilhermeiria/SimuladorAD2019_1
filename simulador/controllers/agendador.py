import random
from math import exp, log

class Agendador(object):

    def __init__(self):
        self.taxa = 0.0

    def setTaxa(self, taxa):
        self.taxa = taxa

    def getSemente(self, range=1):
        semente = random.uniform(0, range)
        while semente == 0:                        # O intervalo da proxima chegada nao pode ser 0.
            semente = random.uniform(0, 1)
        return semente

    def proximoEvento(self):
        u0 = self.getSemente(1)
        a = self.getSemente(100)
        b = self.getSemente(100)

        if u0 < 1 - exp(-self.taxa * a):
            return a
        if u0 > 1 - exp(-self.taxa * b):
            return b

        if (1 - exp(-self.taxa*a) < u0) and (u0 < 1 - exp(-self.taxa*b)):
            x0 = log(1 - u0)/(-self.taxa)
            return x0

# Testando classe
s = Agendador()
tempo_simulacao = s.proximoEvento()
print("Proxima chegada em %f unidades de tempo, tempo de simulacao em: %f" % (tempo_simulacao, tempo_simulacao))
for i in range(100):
    proxima_chegada = s.proximoEvento()
    tempo_simulacao = tempo_simulacao + proxima_chegada
    print("Proxima chegada em %f unidades de tempo, tempo de simulacao em: %f" % (proxima_chegada, tempo_simulacao))