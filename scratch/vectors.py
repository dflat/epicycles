import numpy as np
import matplotlib.pyplot as plt
import math

def vplot(v, tail=[0,0], color='#777777', **kwargs):
    ax.quiver(tail[0], tail[1], v[0], v[1], scale=1,
              scale_units='xy', angles='xy', color=[color], **kwargs)
def clearplot():
    ax.clear()
    equalize_axes()
    ax.scatter(0,0)

def matplot(A, colors=['red','blue'], **kwargs):
    for i in range(len(A.T)):
        vplot(A[:,i], color=colors[i], **kwargs)

def plot_system(A, b):
    clearplot()
    vplot(b,color='#888')
    trace_solution(A, b)
    matplot(A)

def trace_solution(A, b, colors=['#faa','#aaf'], epsilon=0.001):
    basis_vectors = [A[:,i] for i in range(len(A.T))]
    solution_vector = np.linalg.inv(A).dot(b)
    pos = np.zeros(len(A.T)) # To keep track of tail-position of vectors

    for basis_index in range(len(basis_vectors)):
        e = basis_vectors[basis_index]
        coordinate_scalar = solution_vector[basis_index]
        int_part_of_scalar = int(coordinate_scalar)
        fractional_part_of_scalar = coordinate_scalar - int_part_of_scalar
        copies = abs(int_part_of_scalar)

        for i in range(copies):
            length = int_part_of_scalar/copies # Just to get sign data (neg or pos scalar)
            v = length*e
            vplot(v, tail=pos, color=colors[basis_index])
            pos += v

        if abs(fractional_part_of_scalar) > epsilon: 
            length = fractional_part_of_scalar
            v = length*e
            vplot(v, tail=pos, color=colors[basis_index])
            pos += v
    
def vplot(v,tail=[0,0], color='#777777', **kwargs):
    return ax.arrow(tail[0],tail[1],v[0],v[1], head_width=1/10, head_length=2/10,
                    length_includes_head=True, ec=color,fc=color,**kwargs)
    #return ax.quiver(o[0], o[1], v[0], v[1], scale=1,
    #          scale_units='xy', angles='xy', color=[color], **kwargs)
def animate(i):
    print(i)
    #clearplot()
    t = 2*math.pi*i
    b = (3*i/1)*np.array((math.cos(t), math.sin(t)))
    plot_system(A,b)
def run():
    fig, ax = plt.subplots()
    return animation.FuncAnimation(fig, animate, frames=T, blit=False)
