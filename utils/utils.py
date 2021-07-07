import argparse
import json
import os

import torch


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def upload_args_from_json(file_path=os.path.join("parameters", "fixed_params.json")):
    parser = argparse.ArgumentParser(description=f'Arguments from json')
    args = parser.parse_args()
    json_params = json.loads(open(file_path).read())
    for option, option_value in json_params.items():
        if option_value == 'None':
            option_value = None
        setattr(args, option, option_value)
    setattr(args, "runNumber", 0)
    return args


def farthest_and_nearest_points(x, batch_points, n):
    # x should be (batch_size, num_points, 3)
    # batch_points should be (batch_size, 1, 3)
    batch_size = x.size(0)
    num_points = x.size(1)
    assert batch_points.size(0) == batch_size
    assert batch_points.size(2) == 3
    assert batch_points.size(1) == 1
    # batch_points: for each batch (point cloud) we have one point (x,y,z)
    distances = torch.sum((x - batch_points) ** 2, dim=-1)
    idx = distances.topk(k=num_points, dim=-1)[1]
    idx_farthest = idx[:, :n]
    idx_nearest = idx[:, n:]
    idx_base = torch.arange(0, batch_size, device="cuda").view(-1, 1) * num_points
    idx_farthest = (idx_farthest + idx_base).view(-1)
    idx_nearest = (idx_nearest + idx_base).view(-1)
    x = x.view(-1, 3)
    x_far = x[idx_farthest, :]
    x_near = x[idx_nearest, :]
    return x_far.view(batch_size, n, 3), idx_farthest, x_near.view(batch_size, -1, 3)


