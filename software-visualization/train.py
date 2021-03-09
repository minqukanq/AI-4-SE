import argparse
import os

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import network
import loss
import pre_process as prep
import torch.utils.data as util_data
import lr_schedule
from data_list import ImageList
from torch.autograd import Variable
import model_utils
from model_utils import Net
import torch.optim.lr_scheduler as lr_scheduler_torch


optim_dict = {"SGD": optim.SGD}

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

def image_classification_predict(loader, model, test_10crop=True, gpu=True):
    start_test = True
    if test_10crop:
        iter_test = [iter(loader['test'+str(i)]) for i in range(10)]
        for i in range(len(loader['test0'])):
            data = [iter_test[j].next() for j in range(10)]
            inputs = [data[j][0] for j in range(10)]
            if gpu:
                for j in range(10):
                    inputs[j] = Variable(inputs[j].cuda())
            else:
                for j in range(10):
                    inputs[j] = Variable(inputs[j])
            outputs = []
            for j in range(10):
                outputs.append(model(inputs[j]))
            outputs = sum(outputs)
            if start_test:
                all_output = outputs.data.float()
                start_test = False
            else:
                all_output = torch.cat((all_output, outputs.data.float()), 0)
    else:
        iter_val = iter(loader["test"])
        for i in range(len(loader['test'])):
            data = iter_val.next()
            inputs = data[0]
            if gpu:
                inputs = Variable(inputs.cuda())
            else:
                inputs = Variable(inputs)
            outputs = model(inputs)
            if start_test:
                all_output = outputs.data.cpu().float()
                start_test = False
            else:
                all_output = torch.cat((all_output, outputs.data.cpu().float()), 0)
    _, predict = torch.max(all_output, 1)
    return all_output, predict

def image_classification_test(loader, model, test_10crop=True, gpu=True):
    start_test = True
    if test_10crop:
        iter_test = [iter(loader['test'+str(i)]) for i in range(10)]
        for i in range(len(loader['test0'])):
            data = [iter_test[j].next() for j in range(10)]
            inputs = [data[j][0] for j in range(10)]
            labels = data[0][1]
            if gpu:
                for j in range(10):
                    inputs[j] = Variable(inputs[j].cuda())
                labels = Variable(labels.cuda())
            else:
                for j in range(10):
                    inputs[j] = Variable(inputs[j])
                labels = Variable(labels)
            outputs = []
            for j in range(10):
                outputs.append(model(inputs[j]))
            outputs = sum(outputs)

            if start_test:
                all_output = outputs.data.float()
                all_label = labels.data.float()
                start_test = False
            else:
                all_output = torch.cat((all_output, outputs.data.float()), 0)
                all_label = torch.cat((all_label, labels.data.float()), 0)
    else:
        iter_test = iter(loader["test"])
        for i in range(len(loader["test"])):
            data = iter_test.next()
            inputs = data[0]
            labels = data[1]
            if gpu:
                inputs = Variable(inputs.cuda())
                labels = Variable(labels.cuda())
            else:
                inputs = Variable(inputs)
                labels = Variable(labels)
            outputs = model(inputs)
            logits, mlogits = lmcl_loss(outputs, labels)

            if start_test:

                all_output = logits.data.float()
                all_label = labels.data.float()
                # all_output = outputs.data.float()
                # all_label = labels.data.float()
                start_test = False
            else:
                all_output = torch.cat((all_output, logits.data.float()), 0)
                all_label = torch.cat((all_label, labels.data.float()), 0)
                # all_output = torch.cat((all_output, outputs.data.float()), 0)
                # all_label = torch.cat((all_label, labels.data.float()), 0)


    _, predict = torch.max(all_output, 1)
    # accuracy = torch.sum(torch.squeeze(predict).float() == all_label).item() / float(all_label.size()[0])
    accuracy = torch.sum(torch.squeeze(predict).float() == all_label) / float(all_label.size()[0])

    predict_list = predict.cpu().numpy()
    all_label_list = all_label.cpu().numpy()
    TP = 0
    FP = 0
    FN = 0
    for number in range(len(all_label_list)):
        if predict_list[number] == 1:
            if all_label_list[number] == 1:
                TP = TP + 1
            else:
                FP = FP + 1
        elif all_label_list[number] == 1:
            FN = FN + 1

    P = float(TP) / (TP + FP) if (TP + FP != 0) else 0
    R = float(TP) / (TP + FN) if (TP + FN != 0) else 0
    F = float((2 * P * R) / (P + R)) if P + R != 0 else 0
    return accuracy, F

# CenterLoss
# lmcl_loss = model_utils.LMCL_loss(num_classes=2, feat_dim=2).cuda()

def transfer_classification(config):
    ## set pre-process
    prep_dict = {}
    for prep_config in config["prep"]:
        prep_dict[prep_config["name"]] = {}
        if prep_config["type"] == "image":
            prep_dict[prep_config["name"]]["test_10crop"] = prep_config["test_10crop"]
            prep_dict[prep_config["name"]]["train"]  = prep.image_train(resize_size=prep_config["resize_size"], crop_size=prep_config["crop_size"])
            if prep_config["test_10crop"]:
                prep_dict[prep_config["name"]]["test"] = prep.image_test_10crop(resize_size=prep_config["resize_size"], crop_size=prep_config["crop_size"])
            else:
                prep_dict[prep_config["name"]]["test"] = prep.image_test(resize_size=prep_config["resize_size"], crop_size=prep_config["crop_size"])

    ## set loss
    class_criterion = nn.CrossEntropyLoss()


    loss_config = config["loss"]
    transfer_criterion = loss.loss_dict[loss_config["name"]]
    if "params" not in loss_config:
        loss_config["params"] = {}

    ## prepare data
    dsets = {}
    dset_loaders = {}
    for data_config in config["data"]:
        dsets[data_config["name"]] = {}
        dset_loaders[data_config["name"]] = {}
        ## image data
        if data_config["type"] == "image":
            dsets[data_config["name"]]["train"] = ImageList(open(data_config["list_path"]["train"]).readlines(), transform=prep_dict[data_config["name"]]["train"])
            dset_loaders[data_config["name"]]["train"] = util_data.DataLoader(dsets[data_config["name"]]["train"], batch_size=data_config["batch_size"]["train"], shuffle=True, num_workers=4)

            if "test" in data_config["list_path"]:
                if prep_dict[data_config["name"]]["test_10crop"]:
                    for i in range(10):
                        dsets[data_config["name"]]["test"+str(i)] = ImageList(open(data_config["list_path"]["test"]).readlines(), transform=prep_dict[data_config["name"]]["test"]["val"+str(i)]
                                                                              )
                        dset_loaders[data_config["name"]]["test"+str(i)] = util_data.DataLoader(dsets[data_config["name"]]["test"+str(i)], batch_size=data_config["batch_size"]["test"], shuffle=False, num_workers=4)
                else:
                    dsets[data_config["name"]]["test"] = ImageList(open(data_config["list_path"]["test"]).readlines(), transform=prep_dict[data_config["name"]]["test"])
                    dset_loaders[data_config["name"]]["test"] = util_data.DataLoader(dsets[data_config["name"]]["test"], batch_size=data_config["batch_size"]["test"], shuffle=False, num_workers=4)
            else:
                if prep_dict[data_config["name"]]["test_10crop"]:
                    for i in range(10):
                        dsets[data_config["name"]]["test"+str(i)] = ImageList(open(data_config["list_path"]["train"]).readlines(), transform=prep_dict[data_config["name"]]["test"]["val"+str(i)])
                        dset_loaders[data_config["name"]]["test"+str(i)] = util_data.DataLoader(dsets[data_config["name"]]["test"+str(i)], batch_size=data_config["batch_size"]["test"], shuffle=False, num_workers=4)
                else:
                    dsets[data_config["name"]]["test"] = ImageList(open(data_config["list_path"]["train"]).readlines(), transform=prep_dict[data_config["name"]]["test"])
                    dset_loaders[data_config["name"]]["test"] = util_data.DataLoader(dsets[data_config["name"]]["test"], batch_size=data_config["batch_size"]["test"], shuffle=False, num_workers=4)

    class_num = 2

    ## set base network
    net_config = config["network"]
    base_network = network.network_dict[net_config["name"]]()
    if net_config["use_bottleneck"]:
        bottleneck_layer = nn.Linear(base_network.output_num(), net_config["bottleneck_dim"])
        classifier_layer = nn.Linear(bottleneck_layer.out_features, class_num)
    else:
        classifier_layer = nn.Linear(base_network.output_num(), class_num)
    for param in base_network.parameters():
        param.requires_grad = True

    ## initialization
    if net_config["use_bottleneck"]:
        bottleneck_layer.weight.data.normal_(0, 0.005)
        bottleneck_layer.bias.data.fill_(0.1)
        bottleneck_layer = nn.Sequential(bottleneck_layer, nn.ReLU(), nn.Dropout(0.5))
    classifier_layer.weight.data.normal_(0, 0.01)
    classifier_layer.bias.data.fill_(0.0)

    use_gpu = torch.cuda.is_available()
    if use_gpu:
        if net_config["use_bottleneck"]:
            bottleneck_layer = bottleneck_layer.cuda()
        classifier_layer = classifier_layer.cuda()
        base_network = base_network.cuda()


    ## collect parameters
    if net_config["use_bottleneck"]:
        parameter_list = [{"params": base_network.parameters(), "lr": 10},
                          {"params":bottleneck_layer.parameters(), "lr":10},
                          {"params":classifier_layer.parameters(), "lr":10}]

    else:
        parameter_list = [{"params": base_network.parameters(), "lr": 10},
                          {"params":classifier_layer.parameters(), "lr":10}]

    ## set optimizer
    optimizer_config = config["optimizer"]
    optimizer = optim_dict[optimizer_config["type"]](parameter_list, **(optimizer_config["optim_params"]))
    param_lr = []
    for param_group in optimizer.param_groups:
        param_lr.append(param_group["lr"])
    schedule_param = optimizer_config["lr_param"]
    lr_scheduler = lr_schedule.schedule_dict[optimizer_config["lr_type"]]

    ## train
    len_train_source = len(dset_loaders["source"]["train"]) - 1
    len_train_target = len(dset_loaders["target"]["train"]) - 1
    F_best = 0
    mmd_meter = AverageMeter()
    for i in range(config["num_iterations"]):
        ## test in the train
        if i % config["test_interval"] == 0:
            base_network.train(False)
            classifier_layer.train(False)
            if net_config["use_bottleneck"]:
                bottleneck_layer.train(False)
                test_acc, F =  image_classification_test(dset_loaders["target"], nn.Sequential(base_network, bottleneck_layer, classifier_layer), test_10crop=prep_dict["target"]["test_10crop"], gpu=use_gpu)

            else:
                test_acc, F = image_classification_test(dset_loaders["target"], nn.Sequential(base_network, classifier_layer), test_10crop=prep_dict["target"]["test_10crop"], gpu=use_gpu)


            print(args.source + '->' + args.target)
            print('Iter: %d, mmd = %.4f, test_acc = %.3f, f1 score = %.4f' % (i, mmd_meter.avg, test_acc, F))
            mmd_meter.reset()

            if F_best < F:
                F_best = F

        ## train one iter
        if net_config["use_bottleneck"]:
            bottleneck_layer.train(True)
        classifier_layer.train(True)
        optimizer = lr_scheduler(param_lr, optimizer, i, **schedule_param)
        # optimzer4center = optim.SGD(lmcl_loss.parameters(), lr=0.05)
        # sheduler_4center = lr_scheduler_torch.StepLR(optimizer, 20, gamma=0.5)

        # optimizer.zero_grad()
        # optimzer4center.zero_grad()

        if i % len_train_source == 0:
            iter_source = iter(dset_loaders["source"]["train"])
        if i % len_train_target == 0:
            iter_target = iter(dset_loaders["target"]["train"])
        inputs_source, labels_source = iter_source.next()
        inputs_target, labels_target = iter_target.next()

        if use_gpu:
            inputs_source, inputs_target, labels_source = Variable(inputs_source).cuda(), Variable(inputs_target).cuda(), Variable(labels_source).cuda()
        else:
            inputs_source, inputs_target, labels_source = Variable(inputs_source), Variable(inputs_target), Variable(labels_source)

        inputs = torch.cat((inputs_source, inputs_target), dim=0)
        features = base_network(inputs)
        if net_config["use_bottleneck"]:
            features = bottleneck_layer(features)

        outputs = classifier_layer(features)

        #
        # logits, mlogits = lmcl_loss(outputs.narrow(0, 0, int(inputs.size(0)/2)), labels_source)
        # classifier_loss = class_criterion(mlogits, labels_source)

        classifier_loss = class_criterion(outputs.narrow(0, 0, int(inputs.size(0)/2)), labels_source)

        ## switch between different transfer loss
        if loss_config["name"] == "DAN" or loss_config["name"] == "DAN_Linear":
            transfer_loss = transfer_criterion(features.narrow(0, 0, int(features.size(0)/2)), features.narrow(0, int(features.size(0)/2), int(features.size(0)/2)), **loss_config["params"])

        mmd_meter.update(transfer_loss.item(), inputs_source.size(0))
        # mmd_meter.update(transfer_loss.data[0], inputs_source.size(0))
        total_loss = loss_config["trade_off"] * transfer_loss + classifier_loss
        # total_loss = classifier_loss
        total_loss.backward()
        optimizer.step()

        # optimzer4center.step()
        # sheduler_4center.step()

    print(args.source + '->' + args.target)
    print(F_best)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transfer Learning')
    parser.add_argument('--gpu_id', type=str, nargs='?', default='0', help="device id to run")
    parser.add_argument('--source', type=str, nargs='?', default='poi_3.0', help="source data")
    parser.add_argument('--target', type=str, nargs='?', default='ant_1.6', help="target data")
    parser.add_argument('--loss_name', type=str, nargs='?', default='DAN_Linear', help="loss name")
    parser.add_argument('--tradeoff', type=float, nargs='?', default=1, help="tradeoff")
    parser.add_argument('--using_bottleneck', type=int, nargs='?', default=1, help="whether to use bottleneck")
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_id
    path = 'data\\txt\\'

    config = {}
    config["num_iterations"] = 500
    config["test_interval"] = 1
    config["prep"] = [{"name":"source", "type":"image", "test_10crop":False, "resize_size":256, "crop_size":224},
                      {"name":"target", "type":"image", "test_10crop":False, "resize_size":256, "crop_size":224}]
    config["loss"] = {"name":args.loss_name, "trade_off":args.tradeoff }
    config["data"] = [{"name":"source", "type":"image",
                       "list_path": {"train": path + args.source + ".txt"},
                       "batch_size":{"train":64, "test":64} },
                      {"name":"target", "type":"image",
                       "list_path": {"train": path + args.target + ".txt"},
                       "batch_size":{"train":64, "test":64} }]
    config["network"] = {"name":"AlexNet", "use_bottleneck":args.using_bottleneck, "bottleneck_dim":256}
    config["optimizer"] = {"type":"SGD", "optim_params":{"lr":0.05, "momentum":0.9, "weight_decay":0.0005, "nesterov":True},
                           "lr_type":"inv", "lr_param":{"init_lr":0.0003, "gamma":0.0003, "power":0.75} }
    print(config["loss"])
    transfer_classification(config)
