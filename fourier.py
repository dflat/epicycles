import math
import numpy as np
from functools import partial

class FourierTransform:
    def __init__(self, f, n=50, samps=1000, t0=0, t1=1):
        self.cache = { }
        self.f = f
        self.n = n
        self.samps = samps
        self.dt = min(0.01, 1/samps)
        self.t0 = t0
        self.t1 = t1
        self.L = t1 - t0

    def C(self, k):
        integrand = lambda t: self.f(t)*np.exp(complex(0,-2*math.pi*k*t/self.L))
        ck = (1/(self.L/2))*integrate(integrand, self.t0, self.t1, self.dt)
        return ck
    
def CK(f, k, samps=1000, t0=0, t1=1):
    #samps = min(samps, n*2)
    #if (f,n,samps) in cache:
    #    print('got from cache', n)
    #    return cache[(f,n,samps)]
    #print('skipped cache', (f,n,samps))
    L = (t1 - t0)
    dt = min(0.01, 1/samps)
    a0 = (1/(L/2))*integrate(partial(a,k=0,f=f), t0, t1, dt)
    #T = np.linspace(t0,t1,samps)
    #S = np.ones(len(T))*(a0/2)
    ak = (1/(L/2))*integrate(partial(a,k=k,f=f,L=L), t0, t1, dt)
    bk = (1/(L/2))*integrate(partial(b,k=k,f=f,L=L), t0, t1, dt)
    mag = math.sqrt(ak*ak + bk*bk)
    phase = np.arctan2(bk, ak)
    #cache[(f,n,samps)] = (T,S)
    return mag, phase

def F(f, n=50, samps=1000, t0=-math.pi, t1=math.pi):
    samps = min(samps, n*2)
    if (f,n,samps) in cache:
        print('got from cache', n)
        return cache[(f,n,samps)]
    print('skipped cache', (f,n,samps))
    L = (t1 - t0)
    dt = min(0.01, 1/samps)
    a0 = (1/(L/2))*integrate(partial(a,k=0,f=f), t0, t1, dt)
    T = np.linspace(t0,t1,samps)
    S = np.ones(len(T))*(a0/2)
    for k in range(1,n):
        ak = (1/(L/2))*integrate(partial(a,k=k,f=f,L=L), t0, t1, dt)
        bk = (1/(L/2))*integrate(partial(b,k=k,f=f,L=L), t0, t1, dt)
        S += ak*np.cos(2*math.pi*k*T/L) + bk*np.sin(2*math.pi*k*T/L)
    cache[(f,n,samps)] = (T,S)
    return T, S

def F2(f, n=50, sampes=1000, t0=0, t1=1):
    samps = min(samps, n*2)
    L = (t1 - t0)
    dt = min(0.01, 1/samps)



def integrate(f,a,b,dt=0.01):
    s = 0
    n = int((b-a)/dt)
    dt = (b-a)/n
    prev_y = f(a)
    prev_t = a
    dt_half = dt/2
    for i in range(1, n+1):
        t = a + dt*i
        y = f(t)
        s += (prev_y + y)*dt_half
        prev_t = t
        prev_y = y
    return s

def a(t,k,f,L=2*math.pi):
    return f(t)*math.cos(2*math.pi*k*t/L)
def b(t,k,f,L=2*math.pi):
    return f(t)*math.sin(2*math.pi*k*t/L)
    
def ck(k, f):
    g = lambda t: f(t)*np.exp(complex(0,-k*2*np.pi*t))
    return integrate(g, 0, 1, dt=0.001)
    
