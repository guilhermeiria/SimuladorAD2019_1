import random
from math import exp, log

class Agendador(object):

    def __init__(self, lamb=0.8):
        self.lamb = lamb

    def getSemente(self):
        semente = random.uniform(0, 1)
        while semente == 0:
            semente = random.uniform(0, 1)
        return semente

    def proximaChegada(self,tempo_sim=0.0):
        u0 = self.getSemente()
        a = self.getSemente()
        b = self.getSemente()

        if u0 < 1 - exp(-self.lamb * a):
            return a
        if u0 > 1 - exp(-self.lamb * b):
            return b

        if (1 - exp(-self.lamb*a) < u0) and (u0 < 1 - exp(-self.lamb*b)):
            x0 = log(1 - u0)/(-self.lamb)
            return x0

# Testeando classe
s = Agendador()
tempo_sim = s.proximaChegada()
for i in range(10000):
    proxima = s.proximaChegada()
    print('Proxima chegada em: %f segundos' % (proxima))