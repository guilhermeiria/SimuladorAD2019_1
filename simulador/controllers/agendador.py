import random
from math import exp, log

class Agendador(object):

    def __init__(self, taxa=0.8):
        self.taxa = taxa

    def getSemente(self):
        semente = random.uniform(0, 1)
        while semente == 0:                        # O intervalo da proxima chegada nao pode ser 0.
            semente = random.uniform(0, 1)
        return semente

    def proximoEvento(self):
        u0 = self.getSemente()
        a = self.getSemente()
        b = self.getSemente()

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