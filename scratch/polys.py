import numpy as np
from scipy import integrate
from functools import reduce

def poly_eval(C,x):
    return reduce(lambda a,b:x*a+b, reversed(C))

class Poly:
    def __init__(self, coefs, dim=6):
        p = np.array(coefs)
        if len(p) < dim:
            pad = dim - len(p)
            p = np.pad(p, (0,pad)) 
        self.p = p
        self.dim = dim
    
    def eval(self, x):
        return poly_eval(self.p, x)
        
    def dot(self, b:'Poly'):
        p = lambda x: self.eval(x)
        q = lambda x: b.eval(x)
        return Poly._dot(p,q)    
        
    @classmethod
    def _dot(cls, p, q):
        return integrate.quad(lambda t:p(t)*q(t),-1,1)[0]
        
    def __add__(self, b):
        #pad = self.degree - b.degree
        #a = self.p
        #b = b.p
        #if pad > 0:
        #    b = np.pad(b, (0, pad)) 
        #if pad < 0:
        #    a = np.pad(a, (0, abs(pad)))
        return Poly(self.p + b.p, dim=self.dim)
        
    def __sub__(self, b):
        return self.__add__(Poly(-1*b.p, dim=self.dim))
    
    def __mul__(self, c):
        return Poly(self.p*c, dim=self.dim)
        
    def __rmul__(self, c):
        return self.__mul__(c)
           
    def norm(self):
        return np.sqrt(self.dot(self))
    
    def proj_mag(self, v):
        return self.dot(v)/v.dot(v)
        
    def proj(self, v:'Poly'):
        #return (self.dot(v)/v.dot(v))*v
        return self.proj_mag(v)*v
        
    def __call__(self, x):
        return self.eval(x)
        
    def __repr__(self):
        temp = 'Poly<{}>'
        poly = []
        for i in range(self.dim):
            a = self.p[i]
            if a == 0:
                continue
            term = f'{a:.2f}'
            if i > 0 and a == 1:
                term = ""
            if i > 0:
                term += 'x'
            if i > 1:
                term += get_unicode_exponent(i)
            poly.append(term)
        poly = " + ".join(reversed(poly))
        return temp.format(poly)

def plot_legendre(k, n):
    ''' k: number of legendre polynomials to generate,
        n: sampling resolution
        n must be >= k
    '''
    pad = n - k
    L = legendre(k)    
    t = np.linspace(-1,1,n)
    X = vandermonde(t)
    Y = [X.dot(np.pad(L[i].p,(0,pad))) for i in range(k)]
    return [ax.plot(t,Y[i]) for i in range(k)]

def legendre(n, normalize_at_1=True):
    ortho = []
    for i in range(n):
        v = Poly(np.pad([1],(i, n-i-1)), dim=n)
        for V in ortho:
            q = v.proj(V)
            v = v - v.proj(V) 
        ortho.append(v)
    # normalize so each P(1) = 1, since scaling preserves ortho
    if normalize_at_1:
        for i in range(n):
            ortho[i] = ortho[i]*(1/ortho[i](1))
    return ortho

def vandermonde(X):
    n = len(X)
    rows = []
    for i in range(n):
        row = [1]*n
        for j in range(1, n):
            row[j] = X[i]*row[j-1]
        rows.append(row)
    return np.array(rows)

UNICODE_EXP = ['\u2070','\u00b9','\u00b2','\u00b3','\u2074','\u2075',
               '\u2076','\u2077','\u2078','\u2079']
def get_unicode_exponent(n):
    chars = str(n)
    exp = ""
    for c in chars:
        exp += UNICODE_EXP[int(c)]
    return exp


