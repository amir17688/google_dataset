#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import pi, sqrt
from numpy.random import random, seed, randint

#seed(4)

NMAX = 10**7
SIZE = 1080
ONE = 1./SIZE

RAD = 2.5*ONE
H = sqrt(3.)*RAD

STP = ONE
NEARL = RAD*2.
FARL = RAD*30

MID = 0.5

LINEWIDTH = 5.*ONE

BACK = [1,1,1,1]

STEPS_ITT = 10

TWOPI = pi*2.

ZONEWIDTH = 2.*FARL/ONE
NZ = int(SIZE/ZONEWIDTH)
ZMAX = 2000

print 'NZ', NZ
print 'ZMAX', NZ
print 'ZONEWIDTH', ZONEWIDTH

FRONT = [0,0,0,0.6]

CONTRASTA = [0.84,0.37,0,1] # orange
CONTRASTB = [0.53,0.53,1,1] # lightblue
CONTRASTC = [0,0.3,0.3,0.1]
CONTRASTA = [0,0.7,0.8,1]
CONTRASTB = [1,1,1,0.5]


def show(render,edges_coordinates):

  render.clear_canvas()
  render_circles = render.circles

  render_circle = render.circle

  for x1,y1,x2,y2 in edges_coordinates:

    #render_circles(*vv,r=LINEWIDTH*0.5,nmin=2)
    render.ctx.set_source_rgba(*CONTRASTC)
    render_circle(x1,y1,r=FARL)

  for x1,y1,x2,y2 in edges_coordinates:

    render.ctx.set_source_rgba(*FRONT)
    render_circle(x1,y1,r=NEARL)

def steps(dl,steps_itt):

  for i in xrange(steps_itt):

    dl.optimize_position(STP,STP)

    enum = dl.get_enum()

    rnd = random(enum)
    rndmask = (rnd<0.001).nonzero()[0]
    #rndmask = (rnd<0.01).nonzero()[0]
    for e in rndmask:

      l = dl.get_edge_length(e)
      if l<NEARL:
        continue

      e1 = randint(enum)

      try:
        dl.split_edge(e1)
      except ValueError:
        pass


def main():

  import gtk

  from differential import Differential
  from render import Animate
  from time import time
  from helpers import print_stats

  DL = Differential(NMAX, 8, NZ, ZMAX, RAD, NEARL, FARL)

  angles = sorted(random(100)*TWOPI)

  DL.init_circle(MID,MID,RAD*50., angles)

  def wrap(steps_itt, render):

    t1 = time()

    steps(DL,steps_itt)
    edges_coordinates = DL.get_edges_coordinates()
    show(render,edges_coordinates)

    t2 = time()
    print_stats(render.steps, t2-t1, DL)

    return True

  render = Animate(SIZE, BACK, FRONT, STEPS_ITT, wrap)
  render.ctx.set_source_rgba(*FRONT)
  render.ctx.set_line_width(LINEWIDTH)

  gtk.main()


if __name__ == '__main__':

  main()

