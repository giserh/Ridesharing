'''
Created on Mar 12, 2012

@author: Sol
'''

import matplotlib.pyplot as plt
import numpy as np

def randrange(n, vmin, vmax):
    return (vmax-vmin)*np.random.rand(n) + vmin

fig = plt.figure()
ax = fig.gca(projection='3d')


x = np.linspace(0, 1, 100)
y = np.sin(x * 2 * np.pi) / 2 + 0.5
ax.plot(x, y, zs=0, zdir='z', label='zs=0, zdir=z')

colors = ('r', 'g', 'k')
for c in colors:
    x = np.random.sample(20)
    y = np.random.sample(20)
    ax.plot(x, y, 0, 'o-', zdir='y', c=c)

x=np.random.rand(10)
y=np.random.rand(10)
z=np.random.rand(10)

x=range(5)
y=range(5)
z=range(5)




fig1 = plt.figure()
ax = fig1.gca(projection='3d')
n = 100
for c, m, zl, zh in [('r', 'o', -50, -25), ('b', '^', -30, -5)]:
    xs = randrange(n, 23, 32)
    ys = randrange(n, 0, 100)
    zs = randrange(n, zl, zh)
    ax.scatter(xs, ys, zs, c=c, marker=m)
