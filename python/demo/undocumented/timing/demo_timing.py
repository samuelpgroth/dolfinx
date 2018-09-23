# Copyright (C) 2015 Jan Blechta
#
# This file is part of DOLFIN (https://www.fenicsproject.org)
#
# SPDX-License-Identifier:    LGPL-3.0-or-later

from dolfin import *
import numpy as np

# Let's solve some variational problem to get non-trivial timings
mesh = UnitSquareMesh(MPI.comm_world, 32, 32)
V = FunctionSpace(mesh, "Lagrange", 1)
bc = DirichletBC(V, 0.0, lambda x: np.logical_or(np.isclose(x[:,0], 0.0), np.isclose(x[:, 0], 1.0)))
u, v = TrialFunction(V), TestFunction(V)
x = SpatialCoordinate(mesh)
f = 10 * exp(-((x[0] - 0.5) ** 2 + (x[1] - 0.5) ** 2) / 0.02)
g = sin(5*x[0])
a = inner(grad(u), grad(v))*dx
L = f*v*dx + g*v*ds
u = Function(V)
solve(a == L, u, bc)

# List timings; average across processes in parallel
list_timings([TimingType.wall, TimingType.system])

# Get Table object with timings
t = timings([TimingType.wall, TimingType.user, TimingType.system])

# Use different MPI reductions
t_sum = MPI.sum(MPI.comm_world, t)
t_min = MPI.min(MPI.comm_world, t)
t_max = MPI.max(MPI.comm_world, t)
t_avg = MPI.avg(MPI.comm_world, t)

# Print aggregate timings to screen
print('\n'+t_sum.str(True))
print('\n'+t_min.str(True))
print('\n'+t_max.str(True))
print('\n'+t_avg.str(True))

# Store to XML file on rank 0
#if MPI.rank(MPI.comm_world) == 0:
#    f = File(MPI.comm_self, "timings_aggregate.xml")
#    f << t_sum
#    f << t_min
#    f << t_max
#    f << t_avg

# Store timings of each rank separately
#f = File(MPI.comm_self, "timings_rank_%d.xml"
#         % MPI.rank(MPI.comm_world))
#f << t

# Helper function for storing rank-wise average, min and max
# dump_timings_to_xml("timings_avg_min_max.xml")
