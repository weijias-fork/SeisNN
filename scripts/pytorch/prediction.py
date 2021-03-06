import torch
from torch.utils.data import DataLoader

from seisnn.io import get_dir_list
from seisnn.pick import write_probability_pkl
from seisnn.pytorch.dataset import WaveProbDataset
from seisnn.pytorch.model import Nest_Net

pkl_dir = "/mnt/tf_data/pkl/small_set"
pkl_output_dir = pkl_dir + "_predict"
pkl_list = get_dir_list(pkl_dir)

split_point = -100
batch = 512
testset = WaveProbDataset(pkl_list[split_point:], train=False)
testloader = DataLoader(testset, batch_size=batch, shuffle=False, num_workers=2)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = Nest_Net(in_ch=1, out_ch=1)

# if torch.cuda.device_count() > 1:
#     print("Let's use", torch.cuda.device_count(), "GPUs!")
#     model = nn.DataParallel(model)

model.load_state_dict(torch.load('/mnt/tf_data/weights/trained_weight.pt'))
model.eval()
model.to(device)

predict = []
with torch.no_grad():
    for i, data in enumerate(testloader, 0):
        inputs = data
        inputs = inputs.to(device)

        outputs = model(inputs)

        outputs = outputs.cpu()
        outputs = outputs.numpy()

        for trace in outputs:
            predict.append(trace)

write_probability_pkl(predict, pkl_list, pkl_output_dir, remove_dir=True)
