import unittest
import numpy as np
from graspologic.inference import LatentPositionTest
from graspologic.simulations import er_np, sbm


def test_common_input():
    A1 = er_np(20, 0.3)
    A2 = er_np(20, 0.3)

    with pytest.raises(ValueError):
        lpt_function(A1, A2, n_components=-100)
    with pytest.raises(ValueError):
        lpt_function(A1, A2, test_case="oops")
    with pytest.raises(ValueError):
        lpt_function(A1, A2, n_bootstraps=-100)
    with pytest.raises(ValueError):
        lpt_function(A1, A2, embedding="oops")
    with pytest.raises(TypeError):
        lpt_function(A1, A2, n_bootstraps=0.5)
    with pytest.raises(TypeError):
        lpt_function(A1, A2, n_components=0.5)
    with pytest.raises(TypeError):
        lpt_function(A1, A2, embedding=6)
    with pytest.raises(TypeError):
        lpt_function(A1, A2, test_case=6)


def test_n_bootstraps():
    np.random.seed(1234556)
    A1 = er_np(20, 0.3)
    A2 = er_np(20, 0.3)

    _, _, misc_stats = lpt_function(A1, A2, n_bootstraps=234, n_components=None)
    assert misc_stats["null_distribution_1_"].shape[0] == 234


def test_bad_matrix_inputs():
    np.random.seed(1234556)
    A1 = er_np(20, 0)
    A2 = er_np(20, 0)
    A1[2, 0] = 1  # make asymmetric
    with pytest.raises(NotImplementedError):  # TODO : remove when we implement
        lpt_function(A1, A2)

    bad_matrix = [[1, 2]]
    with pytest.raises(TypeError):
        lpt_function(bad_matrix, A2)

    with pytest.raises(ValueError):
        lpt_function(A1[:2, :2], A2)


def test_rotation_norm():
    # two triangles rotated by 90 degrees
    points1 = np.array([[0, 0], [3, 0], [3, -2]])
    rotation = np.array([[0, 1], [-1, 0]])
    points2 = np.dot(points1, rotation)

    n = difference_norm(points1, points2, embeding="ase", test_case="rotation")
    pytest.assertAlmostEqual(n, 0)


def test_diagonal_rotation_norm():
    # triangle in 2d
    points1 = np.array([[0, 0], [3, 0], [3, -2]], dtype=np.float64)
    rotation = np.array([[0, 1], [-1, 0]])
    # rotated 90 degrees
    points2 = np.dot(points1, rotation)
    # diagonally scaled
    diagonal = np.array([[2, 0, 0], [0, 3, 0], [0, 0, 2]])
    points2 = np.dot(diagonal, points2)

    n = difference_norm(points1, points2, embeding="ase", test_case="diagonal-rotation")
    pytest.assertAlmostEqual(n, 0)


def test_scalar_rotation_norm():
    # triangle in 2d
    points1 = np.array([[0, 0], [3, 0], [3, -2]], dtype=np.float64)
    rotation = np.array([[0, 1], [-1, 0]])
    # rotated 90 degrees
    points2 = np.dot(points1, rotation)
    # scaled
    points2 = 2 * points2

    n = difference_norm(points1, points2, embeding="ase", test_case="scalar-rotation")
    pytest.assertAlmostEqual(n, 0)


def test_SBM_epsilon():
    np.random.seed(12345678)
    B1 = np.array([[0.5, 0.2], [0.2, 0.5]])
    B2 = np.array([[0.7, 0.2], [0.2, 0.7]])
    b_size = 200
    A1 = sbm(2 * [b_size], B1)
    A2 = sbm(2 * [b_size], B1)
    A3 = sbm(2 * [b_size], B2)

    p_null, _, _ = lpt_function(A1, A2, n_components=2, n_bootstraps=100)
    p_alt, _, _ = lpt_function(A1, A3, n_components=2, n_bootstraps=100)
    pytest.assertTrue(p_null > 0.05)
    pytest.assertTrue(p_alt <= 0.05)