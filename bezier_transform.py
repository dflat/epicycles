import numpy as np
from typing import List

from svg.path import parse_path
from xml.dom import minidom

def read_svg(svg_filepath):
    doc = minidom.parse(svg_filepath)
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]
    doc.unlink()
    path = parse_path(path_strings[0])
    return path

def get_svg_func(svg_filepath):
    path = read_svg(svg_filepath)
    return lambda t: path.point(t).conjugate() # flip y-axis

def control_point_mat(points):
    return np.array(points).T

def get_Ts(n=100, max_t=1):
    t = np.linspace(0,max_t,n)
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
        self.max_t = 1
        self.cached = None

    def update_controls(self, index, point):
        self.controls.T[index] = point
        self.C = self.controls @ self.B

    def rescale_time(self, factor):
        self.max_t = factor

    def get_point(self, t):
        t = t/self.max_t
        return self.C @ get_mono_t(t)

    def sample(self, n=100, use_cache=True):
        if use_cache and self.cached:
            return self.cached
        self.T = get_Ts(n, max_t=1)
        #self.C = self.controls @ self.B
        self.cached = list(zip((self.C @ self.T).T))
        return self.cached

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

