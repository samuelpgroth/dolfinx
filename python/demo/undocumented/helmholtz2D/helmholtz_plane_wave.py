from dolfin import UnitSquareMesh, MPI, FacetNormal, Expression, \
    FunctionSpace, TrialFunction, TestFunction, dot, inner, dx, ds, \
    grad, Function, solve, interpolate
from dolfin.fem.assembling import assemble
from dolfin.io import XDMFFile
import numpy as np

''' Test Helmholtz problem for which the exact solution is a plane wave
propagating at angle theta to the postive x-axis.
Chosen for comparison with results from Ihlenburg's book
"Finite Element Analysis of Acoustic Scattering" p138-139 '''

# Copyright (C) 2018 Samuel Groth
#
# This file is part of DOLFIN (https://www.fenicsproject.org)
#
# SPDX-License-Identifier:    LGPL-3.0-or-later

# Wavenumber
k0 = 20
# approximation space polynomial degree
deg = 1
# number of elements in each direction of mesh
n_elem = 128

mesh = UnitSquareMesh(MPI.comm_world, n_elem, n_elem)
n = FacetNormal(mesh)

# Incident plane wave
theta = np.pi / 8
ui = Expression(
    'exp(j*k0*(cos(theta)*x[0] + sin(theta)*x[1]))',
    k0=k0,
    theta=theta,
    degree=deg + 3,
    domain=mesh.ufl_domain()
)

# Test and trial function space
V = FunctionSpace(mesh, "Lagrange", deg)

# Define variational problem
u = TrialFunction(V)
v = TestFunction(V)
g = dot(grad(ui), n) + 1j * k0 * ui
a = inner(grad(u), grad(v)) * dx - k0**2 * inner(u, v) * dx + \
    1j * k0 * inner(u, v) * ds
L = inner(g, v) * ds

# Compute solution
u = Function(V)
solve(a == L, u, [])

# Save solution in XDMF format (to be viewed in Paraview, for example)
with XDMFFile(MPI.comm_world, "plane_wave.xdmf",
              encoding=XDMFFile.Encoding.HDF5) as file:
    file.write(u)

''' Calculate L2 and H1 errors of FEM solution and best approximation.
This demonstrates the error bounds given in Ihlenburg.
Pollution errors are evident for high wavenumbers.'''
# Function space for exact solution - need it to be higher than deg
V_exact = FunctionSpace(mesh, "Lagrange", deg + 3)
# "exact" solution
u_exact = interpolate(ui, V_exact)
# best approximation from V
u_BA = interpolate(ui, V)

# H1 errors
diff = u - u_exact
diff_BA = u_BA - u_exact
H1_diff = np.sqrt(assemble(inner(grad(diff), grad(diff)) * dx))
H1_BA = np.sqrt(assemble(inner(grad(diff_BA), grad(diff_BA)) * dx))
H1_exact = np.sqrt(assemble(inner(grad(u_exact), grad(u_exact)) * dx))
print('Relative H1 error of best approximation:', H1_BA / H1_exact)
print('Relative H1 error of FEM solution:', H1_diff / H1_exact)

# L2 errors
L2_diff = np.sqrt(assemble(inner(diff, diff) * dx))
L2_BA = np.sqrt(assemble(inner(diff_BA, diff_BA) * dx))
L2_exact = np.sqrt(assemble(inner(u_exact, u_exact) * dx))
print('Relative L2 error  of best approximation:', L2_BA / L2_exact)
print('Relative L2 error of FEM solution:', L2_diff / L2_exact)
