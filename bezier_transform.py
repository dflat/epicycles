import numpy as np
from typing import List

def control_point_mat(points):
    return np.array(points).T

def get_Ts(n=100):
    t = np.linspace(0,1,n)
    T = []
    for i in range(n):
        ti = t[i]
        T.append((1,ti,ti*ti,ti**3))
    return np.array(T).T#.reshape(4,n)

def get_mono_t(t):
    return np.array((1, t, t*t, t**3))

class Spline:
    B = np.array(((1,-3,3,-1),(0,3,-6,3),(0,0,3,-3),(0,0,0,1))) # bernstein basis
    def __init__(self, control_points: List[float]):
        self.controls = control_point_mat(control_points)
        self.C = self.controls @ self.B

    def get_point(self, t):
        return self.C @ get_mono_t(t)

    def sample(self, n=100):
        self.T = get_Ts(n)
        return self.C @ self.T

#-- point at t: [Control Points][Bernstein Basis][T vector in monomial basis]
#dims: [2 x 1]: [ 2 x 4 ]       [ 4 x 4 ]         [ 4 x 1 ]
if __name__ == '__main__':
    # example cubic bezier curve
    points = control_point_mat(((1,1),(2,-1),(3,4),(4,1))) # cubic control points
    B = np.array(((1,-3,3,-1),(0,3,-6,3),(0,0,3,-3),(0,0,0,1))) #bernstein basis 
    C = points@B
    Ts = get_Ts(10)
    POINTS = C@Ts

def example_curve(): # "infinity symbol" like shape
    controls = np.array([(-3,0),(-3,3),(3,-3),(3,0)])
    controls_b = np.array([(3,0),(3,3),(-3,-3),(-3,0)]) 
    s1 = Spline(controls)
    s2 = Spline(controls_b)
    def P(t: float) -> complex:
        # trace two splines for t in (0..1)
        if t <= 0.5:
            return complex(*s1.get_point(2*t))
        else:
            return complex(*s2.get_point(2*t - 1))
    return P        

