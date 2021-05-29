import numpy as np
import matplotlib.pyplot as plt

#Insert the cloud path in order to print it
def printCloud(cloud):
        alpha = 0.5
        xyz = np.loadtxt(cloud)
        print(xyz)
        fig = plt.figure(figsize=(15, 15))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], 'o', alpha=alpha)
        plt.show()