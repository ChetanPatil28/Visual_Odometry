import cv2
import numpy as np
import utils
np.random.seed(79)
# np.set_printoptions(precision=4)
np.set_printoptions(precision=3)

Points = np.random.randint(11, 50, size=(8, 3)) # 8-points
K = np.load("../camMatrix_720p.npy")
dist = np.zeros(shape=5)



########################################## Case-1 ########################################## 
## Here we shall place two cameras, one at origin and the other somehwere ie R2 and X_cam2.
## We shall manually project a set of 3d points on two different cameras.
## We shall use the 2d-projected points from both the cameras, calculate the Essential-Mat, get the R and t.
## This R and t from essential must be same as our predefined R2, t2.

# This is the first camera with same orientation and same place as origin.
X_cam1 = np.asarray([0, 0, 0]).reshape(3, -1)
R1 = utils.rotate()
t1 = -R1.dot(X_cam1) # t will be R_transpose.cam-centre

P1 = utils.P_from_krt(K, R1, t1)
pts2d_1 = utils.project(P1, Points)
pts2d_1 = utils.hom_to_euc(pts2d_1)
# print("Finally points are ", pts2d_1)
    

# This is the 2nd camera oriented and shifted to some other place.
X_cam2 = np.asarray([10, 25, 7]).reshape(3, -1)
R12 = utils.rotate(thetax=49)
t12 = -R12.dot(X_cam2) # t1 will be R_transpose.cam-centre . t2 is essentially location of cam1 wrt cam2.
t12_norm = t12/np.linalg.norm(t12)

P2 = utils.P_from_krt(K, R12, t12)
pts2d_2 = utils.project(P2, Points)
pts2d_2 = utils.hom_to_euc(pts2d_2)

Ess1, _ = cv2.findEssentialMat(pts2d_1, pts2d_2, K ,cv2.FM_RANSAC)
R12_est1, R12_est2, t12_est = cv2.decomposeEssentialMat(Ess1) # t2_est shall be a unit-vector. it wont give the legth, but only dir.

print("R estimated is equal ???  ", (R12-R12_est1).sum(), np.allclose(R12, R12_est2))
print("Is the t equal ??? ", np.allclose(t12_norm, t12_est))

#### As you see above, both the `t` as well as `Rs` estimated by opencv are very close-by.


########################################## Case-2 ########################################## 
## Here we shall place two cameras, one with R2, t2 and other with R3, t3
## We shall manually project a set of 3d points on these two cameras.
## we shall do the same things as we did above.
## Except that these R  and t will be the ones wrt the first-camera.


X_cam3 = np.asarray([15, 25, 9]).reshape(3, -1)
R13 = utils.rotate(thetay=68)
t13 = -R13.dot(X_cam3) # t will be R_transpose.cam-centre
t13_norm = t13/np.linalg.norm(t13)

P3 = utils.P_from_krt(K, R13, t13)
pts2d_3 = utils.project(P3, Points)
pts2d_3 = utils.hom_to_euc(pts2d_3)

Ess2, _ = cv2.findEssentialMat(pts2d_2, pts2d_3, K ,cv2.FM_RANSAC)
R23_est1, R23_est2, t23_est = cv2.decomposeEssentialMat(Ess2) # t3_est shall be a unit-vector. it wont give the legth, but only direction.


## Note that these R3_est1 or R3_est2 will give you the rotation of Cam3 wrt to Cam2. (assuming that cam2 was at rotation=0).



#### Now let's see how we can get the rotation of Cam3 wrt Cam1(the original origin).
## One way to get this is by findng the essential matrix and then decomposing using pts2d_1 and pts2d_3.

# HOW TO DO THIS ?
# wkt, R2 orients from cam1(origin) to cam2. And R3_est1 orients from cam2 to cam3.
# Then,we can simply orient from cam3 to cam2 using `R3_est1.transpose()`. and then from cam2 to cam1 using (R2_est1.transpose())

# But how do we know if the above steps are correct. Just use essential mat from `pts2d_1` and `pts2d_3` , 
# get the rotation-mat and verify.

Ess3, _ = cv2.findEssentialMat(pts2d_1, pts2d_3, K ,cv2.FM_RANSAC)
R13_est1, R13_est2, t13_est = cv2.decomposeEssentialMat(Ess3) # t_est shall be a unit-vector. it wont give the legth, but only direction.

# lets see in code.
# R_13 means orientation of cam3 wrt cam1. Think why there is .T in the end :-)
R_13_calc = np.matmul(R12_est1.T, R23_est1.T).T # because without the .T , it will give R31.
print((R13_est1 - R_13_calc).sum())
# As we see, the difference between both is of order 10e-8.



## Brainstorm question.
# R12 orients from Cam1 to Cam2,
# R23 orients from Cam2 to Cam3.
# R13 orients from Cam1 to Cam3.

# U are given only R12 and R13 , find R23.
# lets put some points before solving.

## R13 = R12 * R23 Pre-multiply by R12.T ie R21 we will get,
## R12.T * R13  = R12.T R12 * R23
## R12.T * R13  = R23.


print("R23 is ", np.matmul(R12.T, R_13_calc), "\n", R13)





#### Now, we are done with ROTATIONS. Lets now deal with TRANSLATIONS.
 

############################################

# Lets get cam-centre directions of all cameras from the estimated ts.


Cam2_est = -R12_est1.T.dot(t12_est)
Cam3_est = -R13_est1.T.dot(t13_est)
print("Cam2 \n", Cam2_est, np.allclose(Cam2_est, X_cam2/np.linalg.norm(X_cam2)))
print("Cam3 \n", Cam3_est, np.allclose(Cam3_est, X_cam3/np.linalg.norm(X_cam3)))


Cam23_est = -R12.T.dot(-R23_est1.T.dot(t23_est))
X_cam23 = X_cam3 - X_cam2
print("Xcam23-norm will be ", (X_cam23/np.linalg.norm(X_cam23) - Cam23_est).sum())

# print("Cam3 wrt cam2 ",Cam23_est, R3_est1.dot(Cam2_est), Cam3_est - Cam2_est )












