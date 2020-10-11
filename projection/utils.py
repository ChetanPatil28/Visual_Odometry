import cv2
import numpy as np

class Camera:
    def __init__(self, K=np.eye(3), Rc=np.eye(3), center=np.zeros((3, 1))):
        self.K = K
        self.Rc = Rc
        self.R = Rc.T
        self.center = center
        self.t = -self.R.dot(self.center)
        self.Rt = np.hstack((self.R, self.t))
        self.P = P_from_krt(self.K, self.R, self.t)

    def norm(self, vec):
        return vec / np.linalg / norm(vec)

def rotate(thetax=0, thetay=0, thetaz=0):
    th_x, th_y, th_z = np.deg2rad(thetax), np.deg2rad(thetay), np.deg2rad(thetaz)
    R, _  = cv2.Rodrigues(np.asarray([th_x, th_y, th_z], dtype=np.float32))
    return R


def project(P_Mat, points_3d):
    ones = np.ones(points_3d.shape[0]).reshape(-1, 1)
    points_3d = euc_to_hom(points_3d)
    points_3d_homo = np.transpose(points_3d, axes=(1, 0) )
    points_2d_homo = np.matmul(P_Mat, points_3d_homo).T # convert to (N, 3) by trnasposing.
    return points_2d_homo

def euc_to_hom(points): # (N, 2 or 3)
    ones = np.ones(points.shape[0]).reshape(-1, 1)
    points_homo = np.concatenate((points, ones), axis = 1)
    return points_homo


def hom_to_euc(points): # (N, 3 or 4)
    last = points[:, -1].copy()
    points_euc = points/last[:, None]
    return points_euc[:, :-1]


def P_from_krt(K, R, t):
    Rt = np.hstack((R, t))
    P = np.matmul(K, Rt)
    return P

def norm(vec):
    return vec/np.linalg.norm(vec)
