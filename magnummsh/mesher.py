# Copyright (C) 2011-2015 Claas Abert
#
# This file is part of magnum.msh. 
#
# magnum.msh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# magnum.msh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with magnum.msh. If not, see <http://www.gnu.org/licenses/>.
# 
# Last modified by Claas Abert, 2015-06-08

from __future__ import absolute_import 
import magnummsh.cpp as cpp
import dolfin
import numpy
import re

__all__ = ["Mesher", "Mesh"]

class Mesher(cpp.Mesher):
  """
  This class uses the Gmsh library to generate dolfin meshes.
  It provides methods to surround arbitrary meshes with a cuboid shell
  as required by the shell-transformation method, see
  :ref:`shell-transformation`. Moreover regular cuboid meshes can
  be created and domain information can be attached to the resulting
  dolfin mesh.
  
  The shell is always created symmetrically around the coordinate
  origin. Hence mesh files read by this class should also be constructed
  symmetrically around the origin.
  
  *Example*
  
    .. code-block:: python

      # Read sample.msh and create shell
      mesher = Mesher()
      mesher.read_file("sample.msh")
      mesher.create_shell(2, 0.1, (10, 10, 10));
      mesh = mesher.mesh()

      # Create cuboid mesh and surround with shell
      mesher = Mesher()
      mesher.create_cuboid((100.0, 100.0, 5.0), (20, 20, 1))
      mesher.create_shell(2);
      mesh = mesher.mesh()
  """

  def __init__(self):
    super(Mesher, self).__init__()
    self._celldomains = []
    self._facetdomains = []

  def create_cuboid(self, size, n):
    """
    Creates a cuboid of given dimension and discretization around the coordinate
    origin.
    
    *Arguments*
      size (:class:`[float]`)
        Size of the cuboid.
      n (:class:`[int]`)
        Number of mesh mesh intervals.
    """

    return super(Mesher, self).create_cuboid(
        numpy.array(size, dtype="d"),
        numpy.array(n, dtype="i")
    )

  def create_celldomain(self, domain, domain_id):
    """
    Create a cell domain and attach it as :class:`dolfin.MeshDomains` object to the mesh.

    *Arguments*
      domain (:class:`dolfin.SubDomain`)
        The subdomain to be marked
      domain_id (:class:`int`)
        The id of the subdomain
    """
    # keep reference to domain to avoid DirectorMethodException
    self._celldomains.append(domain)
    return super(Mesher, self).create_celldomain(domain, domain_id)

  def create_facetdomain(self, domain, domain_id):
    """
    Create a facet domain and attach it as :class:`dolfin.MeshDomains` object to the mesh.

    *Arguments*
      domain (:class:`dolfin.SubDomain`)
        The subdomain to be marked
      domain_id (:class:`int`)
        The id of the subdomain
    """
    # keep reference to domain to avoid DirectorMethodException
    self._facetdomains.append(domain)
    return super(Mesher, self).create_facetdomain(domain, domain_id)

  def create_shell(self, d, margin = 0.0, n = (0,0,0), progression = 1.0):
    """
    Creates a cuboid shell around the current sample.
    
    *Arguments*
      d (:class:`int`)
        Number of layers of the shell mesh.
      margin (:class:`float`)
        Margin between sample and shell
        (useful for meshes read from file).
      n (:class:`[int]`)
        Number of mesh points of shell.
        (only required if mesh was read from file)
      progression (:class:`float`)
        Defines coarsening of the shell layers.
        1.0 means no coarsening.
    """

    return super(Mesher, self).create_shell(d, margin, numpy.array(n, dtype="i"), progression)

  def mesh(self, scale = 1.0, mesh = None):
    """
    Mesh the geometry and return as :class:`dolfin.Mesh` object with domains
    attached as :class:`dolfin.MeshDomains`.
    
    *Arguments*
      scale (:class:`float`)
        Scaling of the mesh.
      mesh (:class:`float`)
        Optional mesh to write to

    *Returns*
      :class:`dolfin.Mesh`
        The dolfin mesh.
    """

    if mesh is None: mesh = dolfin.Mesh()
    super(Mesher, self).mesh(mesh, scale)
    return mesh

  def get_sample_size(self, i = None, scale = 1.0):
    """
    Returns the sample size (inner-shell size) in a given
    dimension. Scaling used for mesh generation is not considered.
    If no direction is specified a list of sizes is returned.
    
    *Arguments*
      i (:class:`int`)
        The dimension (direction).
      scale (:class:`float`)
        Scaling of the mesh.
    *Returns*
      :class:`int` / :class:`[int]`
        The sample size (Either a single value or a tuple)
    """

    if i is not None:
      return super(Mesher, self).get_sample_size(i) * scale

    # return array if if no component is given
    size = []
    for i in range(3):
      size.append(super(Mesher, self).get_sample_size(i) * scale)

    return size

def Mesh(*args, **kwargs):
  if len(args) == 1 and not re.match(r'.*[.]xml$', args[0]):
    mesher = Mesher()
    mesher.read_file(args[0])
    return mesher.mesh()
  else:
    return dolfin.Mesh(*args, **kwargs)
