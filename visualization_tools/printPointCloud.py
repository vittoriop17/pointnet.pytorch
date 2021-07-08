import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib import gridspec
import utils.dataset as ds
import torch
from utils.dataset_seg import ShapeNetPart
from train_pc import cropping


# Insert the cloud path in order to print it
def printCloudFile(cloud_original, cloud_decoded, name):
    alpha = 0.5
    xyz = np.loadtxt(cloud_original)
    # print(xyz)
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], 'o', alpha=alpha)
    ax.set_title("original cloud")
    ax.append(fig.add_subplot(111, projection='3d'))

    ax[-1].plot(cloud_decoded[:, 0], cloud_decoded[:, 1], cloud_decoded[:, 2], 'o', alpha=alpha)
    ax[-1].set_title("decoded cloud")
    plt.savefig(f"/content/pointnet.pytorch/{name}.png")


def printCloud(cloud_original, name, alpha=0.5, opt=None):
    xyz = cloud_original[0]
    print("sono qui")
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], 'o', alpha=alpha)
    ax.set_title("original cloud")
    folder = "/content/pointnet.pytorch/images/" if opt is None else os.path.join(opt.outf, "images")
    try:
        os.makedirs(folder)
    except OSError:
        pass
    plt.savefig(os.path.join(folder, f"{hash(str(opt))}_{name}.png"))


def printCloudM(cloud_original, cloud_decoded, name, alpha=0.5, opt=None):
    xyz = cloud_original[0]
    fig = plt.figure(figsize=(30, 15))
    ax = fig.add_subplot(1, 2, 1, projection='3d')
    ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], 'o', alpha=alpha)
    ax.set_title("original cloud")
    xyz = cloud_decoded[0]
    ax = fig.add_subplot(1, 2, 2, projection='3d')
    ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], 'o', alpha=alpha)
    ax.set_title("decoded cloud")
    folder = "/content/pointnet.pytorch/images/" if opt is None else os.path.join(opt.outf, "images")
    try:
        os.makedirs(folder)
    except OSError:
        pass
    plt.savefig(os.path.join(folder, f"{hash(str(opt))}_{name}.png"))


def savePtsFile(type, category, opt, array, run=None):
    folder = os.path.join(opt.outf, "visualizations", f"{opt.runNumber}", category)
    string_neptune_path = f"point_clouds/{category}/{type}"
    try:
        os.makedirs(folder)
    except OSError:
        pass
    pc_file = open(os.path.join(folder, f"{type}.pts"), 'w')
    np.savetxt(pc_file, array)
    if run is not None:
        run[string_neptune_path].upload(pc_file.name)
    pc_file.close()


def print_original_decoded_point_clouds(dataset, category, model, opt, run=None):
    categories = [category]
    if category is None:
        categories = dataset.get_categories()
    for category in categories:
        n_point_clouds = 30 if hasattr(opt, 'novel_categories') else 10
        for index in range(n_point_clouds):
            point_cloud = dataset.get_point_cloud_by_category(category, index=index)
            model.eval()
            point_cloud_np = point_cloud.cuda()
            point_cloud_np = torch.unsqueeze(point_cloud_np, 0)
            decoded_point_cloud = model(point_cloud_np)
            if opt.type_decoder == "pyramid":
                decoded_point_cloud = decoded_point_cloud[2]  # take only the actual input reconstruction
            original_pc_np = point_cloud_np.cpu().numpy()
            decoded_pc_np = decoded_point_cloud.cpu().data.numpy()
            # printCloudM(point_cloud_np, dec_val_stamp, name=category, opt=opt)
            original_pc_np = original_pc_np.reshape((1024, 3))
            decoded_pc_np = decoded_pc_np.reshape((1024, 3))
            savePtsFile(f"original_n{index}", category, opt, original_pc_np, run)
            savePtsFile(f"decoded_n{index}", category, opt, decoded_pc_np, run)


def print_original_incomplete_decoded_point_clouds(category, model, opt, run):
    categories = ["airplane", "car", "chair", "lamp", "mug", "motorbike", "table"]\
        if category is None else [category]
    model.eval()
    for category in categories:
        dataset = ShapeNetPart(root=opt.dataset, class_choice=category, split="test")
        for index in range(10):
            if index > dataset.__len__():
                break
            point_cloud = dataset.__getitem__(index)
            point_cloud = point_cloud.cuda()
            point_cloud = torch.unsqueeze(point_cloud, 0)
            original_pc_np = point_cloud.cpu().numpy()
            original_pc_np = original_pc_np.reshape((-1, 3))
            savePtsFile(f"{index}_original", category, opt, original_pc_np, run)
            for num_crop in range(5):
                incomplete_cloud, _ = cropping(point_cloud)
                incomplete_cloud = incomplete_cloud.cuda()
                if opt.segmentation:
                    decoded_point_cloud, pred = model(incomplete_cloud)
                    decoded_point_cloud = decoded_point_cloud[2]
                else:
                    decoded_point_cloud = model(incomplete_cloud)
                decoded_pc_np = decoded_point_cloud.cpu().data.numpy()
                incomplete_pc_np = incomplete_cloud.cpu().data.numpy()
                incomplete_pc_np = incomplete_pc_np.reshape((-1, 3))
                decoded_pc_np = decoded_pc_np.reshape((-1, 3))
                savePtsFile(f"{index}_{num_crop}_incomplete", category, opt, incomplete_pc_np, run)
                savePtsFile(f"{index}_{num_crop}_decoded", category, opt, decoded_pc_np, run)
