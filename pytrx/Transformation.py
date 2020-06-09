# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 17:33:17 2016

@author: darren

A library of predefined moves for the Molecule class.

"""

import numpy as np
import math
from pytrx.utils import AtomicMass

class transformation_move_vector:
    # Move a group of atoms along a vector (normalized)
    def __init__(self, group1, vector, amplitude0=0):
        self.group1 = np.array(group1)
        self.vector = np.array(vector)
        self.unit_vector = np.array(vector) / np.linalg.norm(vector)
        self.amplitude0 = amplitude0

    def prepare(self, mol):
        assert (np.max(self.group1) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 1 > length of supplied molecule"
        return self

    def describe(self):
        print("  Moving group1 along a predefined vector. Both groups move.")
        print(f'    Group 1: {self.group1}')
        print(f'    Vector : {self.unit_vector}')

    def transform(self, xyz, amplitude=None):

        if amplitude is None:
            amplitude = self.amplitude0
        xyz[self.group1] += self.unit_vector * amplitude
        return xyz


class transformation_vibration:
    def __init__(self, dxyz, amplitude0=0):
        self.dxyz = dxyz
        self.amplitude0 = amplitude0

    def prepare(self, mol):
        assert self.dxyz.shape[0] == mol.xyz.shape[0], \
            'number of atoms in transformation and in the molecule must match'
        return self

    def describe(self):
        print("Move all atoms along a predefined vibrational mode.")

    def transform(self, xyz, amplitude=None):
        if amplitude is None:
            amplitude = self.amplitude0
        return (xyz + self.dxyz * amplitude)





class transformation_distance:
    # Move two groups of atoms closer/further in distance, using simple mean of coordinates as
    # reference centers for each group.
    # Vector is from group1 to group2. Negative amplitude is shrinking.
    def __init__(self, group1, group2, amplitude0=0):
        assert (len(group1) > 0) and (len(group2) > 0), 'Cannot operate on empty set'
        self.group1 = np.array(group1)
        self.group2 = np.array(group2)
        self.amplitude0 = amplitude0

    def prepare(self, mol):
        assert (np.max(self.group1) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 1 > length of supplied molecule"
        assert (np.max(self.group2) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 2 > length of supplied molecule"
        self.group1_mean = np.mean(mol.xyz[self.group1], 0)
        self.group2_mean = np.mean(mol.xyz[self.group2], 0)
        self.unit_vec = (self.group2_mean - self.group1_mean) / np.linalg.norm(self.group2_mean - self.group1_mean)
        return self

    def describe(self):
        print(f'  Increasing / decreasing distance between group1 and group2 using '
              f'simple mean of coordinates as centers.\n'
              f'  Both groups move.')
        print(f'    Group 1: {self.group1}')
        print(f'    Group 2: {self.group2}')

    def transform(self, xyz, amplitude=None):

        if amplitude is None:
            amplitude = self.amplitude0

        xyz[self.group1] -= self.unit_vec * amplitude / 2
        xyz[self.group2] += self.unit_vec * amplitude / 2

        return xyz


class transformation_distance_1side:
    # Move GROUP 2 toward/away from GROUP 1 in distance, using simple mean of coordinates as
    # reference centers for each group.
    # Vector is from group1 to group2. Negative amplitude is shrinking.
    # GROUP 1 is fixed.
    def __init__(self, group1, group2, amplitude0=0):
        assert (len(group1) > 0) and (len(group2) > 0), 'Cannot operate on empty set'
        self.group1 = np.array(group1)
        self.group2 = np.array(group2)
        self.amplitude0 = amplitude0

    def prepare(self, mol):
        assert (np.max(self.group1) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 1 > length of supplied molecule"
        assert (np.max(self.group2) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 2 > length of supplied molecule"
        self.group1_mean = np.mean(mol.xyz[self.group1], 0)
        self.group2_mean = np.mean(mol.xyz[self.group2], 0)
        self.unit_vec = (self.group2_mean - self.group1_mean) / np.linalg.norm(self.group2_mean - self.group1_mean)
        return self

    def describe(self):
        print(f'  Increasing / decreasing distance between group1 and group2 using '
              f'simple mean of coordinates as centers.\n' 
              f'  Only group 2 moves.')
        print(f'    Group 1: {self.group1}')
        print(f'    Group 2: {self.group2}')

    def transform(self, xyz, amplitude=None):
        if amplitude is None:
            amplitude = self.amplitude0

        xyz[self.group2] += self.unit_vec * amplitude / 2

        return xyz

class transformation_distanceCOM:
    # Move two group of atoms closer/further in distance, using center of mass as ref centers for each group
    # Vector is from group1 to group2. Negative amplitude is shrinking.
    def __init__(self, group1, group2, amplitude0=0):
        assert (len(group1) > 0) and (len(group2) > 0), 'Cannot operate on empty set'
        self.group1 = np.array(group1)
        self.group2 = np.array(group2)
        self.amplitude0 = amplitude0

    def prepare(self, mol):
        assert (np.max(self.group1) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 1 > length of supplied molecule"
        assert (np.max(self.group2) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 2 > length of supplied molecule"
        self.group1_Mass = np.sum(AtomicMass()[mol.Z_num[self.group1] - 1])
        self.group1_COM = np.sum(mol.xyz[self.group1].T * AtomicMass()[mol.Z_num[self.group1] - 1], 1) / self.group1_Mass
        self.group2_Mass = np.sum(AtomicMass()[mol.Z_num[self.group2] - 1])
        self.group2_COM = np.sum(mol.xyz[self.group2].T * AtomicMass()[mol.Z_num[self.group2] - 1], 1) / self.group2_Mass
        self.unit_vec = (self.group2_COM - self.group1_COM) / np.linalg.norm(self.group2_COM - self.group1_COM)
        self.unit_vec = self.unit_vec.T
        return self

    def describe(self):
        print(f'  Increasing / decreasing distance between group1 and group2 using centers of masses as centers.\n'
              f'  Both groups move.')
        print(f'    Group 1: {self.group1}')
        print(f'    Group 2: {self.group2}')

    def transform(self, xyz, amplitude=None):

        if amplitude is None:
            amplitude = self.amplitude0

        xyz[self.group1] -= self.unit_vec * amplitude / 2
        xyz[self.group2] += self.unit_vec * amplitude / 2

        return xyz


class transformation_distanceCOM_1side:
    # Move GROUP 2 toward/away from GROUP 1 in distance, using center of mass as ref centers for each group
    # Vector is from group1 to group2. Negative amplitude is shrinking.
    # GROUP 1 is fixed.
    def __init__(self, group1, group2, amplitude0=0):
        assert (len(group1) > 0) and (len(group2) > 0), 'Cannot operate on empty set'
        self.group1 = np.array(group1)
        self.group2 = np.array(group2)
        self.amplitude0 = amplitude0

    def prepare(self, mol):
        assert (np.max(self.group1) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 1 > length of supplied molecule"
        assert (np.max(self.group2) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 2 > length of supplied molecule"
        self.group1_Mass = np.sum(AtomicMass()[mol.Z_num[self.group1] - 1])
        self.group1_COM = np.sum(mol.xyz[self.group1].T * AtomicMass()[mol.Z_num[self.group1] - 1],
                                 1) / self.group1_Mass
        self.group2_Mass = np.sum(AtomicMass()[mol.Z_num[self.group2] - 1])
        self.group2_COM = np.sum(mol.xyz[self.group2].T * AtomicMass()[mol.Z_num[self.group2] - 1],
                                 1) / self.group2_Mass
        self.unit_vec = (self.group2_COM - self.group1_COM) / np.linalg.norm(self.group2_COM - self.group1_COM)
        self.unit_vec = self.unit_vec.T
        return self

    def describe(self):
        print(f'  Increasing / decreasing distance between group1 and group2 using centers of masses as centers.\n'
              f'  Only group 2 moves.')
        print(f'    Group 1: {self.group1}')
        print(f'    Group 2: {self.group2}')

    def transform(self, xyz, amplitude=None):

        if amplitude is None:
            amplitude = self.amplitude0

        xyz[self.group2] += self.unit_vec * amplitude

        return xyz

class transformation_rotation:
    def __init__(self, group1, axis_groups, amplitude=0):
        # A, B, and C can be group of atoms.
        # Centers will be the mean of their coordinates.
        # If axis is length 2 (AB), use vector AB as the rotation axis
        # If axis is length 3 (ABC), use the center of central group as the center,
        # the cross vector of AB and BC as axis.
        # Amplitude is in degrees
        # Rotation is counterclockwise for an observer to whom the axis vector is pointing (right hand rule)
        assert (len(group1) > 0) and (len(axis_groups) > 0), 'Cannot operate on empty set'
        assert (len(axis_groups) == 2) or (len(axis_groups) == 3), 'Axis must be defined with 2 or 3 groups'
        for i in np.arange(len(axis_groups)):
            assert (len(axis_groups[i]) > 0), f'Axis group {i} is empty'

        self.group1 = group1
        self.axis_groups = axis_groups

    def prepare(self, mol):
        assert (np.max(self.group1) <= len(mol.xyz)), \
            "Index out of bound: largest index of group 1 > length of supplied molecule"
        for i in np.arange(len(self.axis_groups)):
            assert (np.max(self.axis_groups) <= len(mol.xyz)), \
                "Index out of bound: largest index of group 1 > length of supplied molecule"
        self.A_mean = np.mean(mol.xyz[self.axis_groups[0]], 0)
        self.B_mean = np.mean(mol.xyz[self.axis_groups[1]], 0)
        if len(self.axis_groups) == 3:
            self.C_mean = np.mean(mol.xyz[self.axis_groups[2]], 0)

        if len(self.axis_groups) == 2: # Then use AB as vector
            self.axis = self.B_mean - self.A_mean

        if len(self.axis_groups) == 3: # Use cross product of AB and BC as vector
            self.axis = np.cross(self.B_mean - self.A_mean, self.C_mean - self.B_mean)

        return self

    def describe(self):
        pass

    def transform(self, xyz, amplitude=None):
        if amplitude is None:
            amplitude = self.amplitude0

        xyz[self.group1] = rotation3D(xyz[self.group1].T, self.axis, amplitude).T

        return xyz

class transformation_rotationCOM:
    def __init__(self, group1, axis, amplitude=0):
        # A, B, and C can be group of atoms.
        # Centers will be the COM of their coordinates.
        # If axis is length 2 (AB), use vector AB as the rotation axis
        # If axis is length 3 (ABC), use the COM of central group as the center,
        # the normal vector of BA and BC as axis
        # Amplitude is in degrees
        pass


def rotation3D(v, axis, degrees):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians. Using the Euler-Rodrigues formula:
    https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    theta = degrees * math.pi / 180
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    rot_mat = np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    return np.dot(rot_mat, v)
