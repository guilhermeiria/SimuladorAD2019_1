import math

class Calculadora(object):

    def __init__(self, intervaloDeConfianca):
        # intervaloDeConfianca
        self.ic = intervaloDeConfianca
        self.k = self.n = self.ex = self.ex2 = 0.0

    '''
    K = n = Ex = Ex2 = 0.0

    def add_variable(x):
        if (n == 0):
            K = x
        n = n + 1
        Ex += x - K
        Ex2 += (x - K) * (x - K)

    def remove_variable(x):
        n = n - 1
        Ex -= (x - K)
        Ex2 -= (x - K) * (x - K)

    def get_meanvalue():
        return K + Ex / n

    def get_variance():
        return (Ex2 - (Ex*Ex)/n) / (n-1)
    '''
    def adicionaValor(self, x):
        if (self.n == 0):
            self.k = x
        self.n += 1
        self.ex += x - self.k
        self.ex2 += (x - self.k) * (x - self.k)

    def get_media(self):
        return self.k + self.ex / self.n

    def get_variancia(self):
        return (self.ex2 - (self.ex*self.ex)/self.n) / (self.n-1)