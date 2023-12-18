
import torch
import torchaudio.transforms
from torch import nn
from torch.utils.data import DataLoader

from urbansounddataset import UrbanSoundDataset
from cnn import CNNNetwork

BATCH_SIZE = 128
EPOCHS = 10
LEARNING_RATE = 0.001

ANNOTATIONS_FILE = "dl_dataset/metadata/UrbanSound8K.csv"
AUDIO_DIR = "dl_dataset/audio"
SAMPLE_RATE = 22050
NUM_SAMPLES = 22050


def train_one_epoch(model, data_loader, loss_fn, optimizer, device):
    for inputs, targets in data_loader:
        inputs, targets = inputs.to(device), targets.to(device)

        # calculate loss
        predictions = model(inputs)
        loss = loss_fn(predictions, targets)

        # backpropagate loss and update weights
        optimizer.zero_grad()
        loss.backward()    # applies backprop
        optimizer.step()    # final step updates weights

    print(f"Loss: {loss.item()}") # printing the loss for the last batch that we have


def train(model, data_loader, loss_fn, optimizer, device, epochs):
    for i in range(epochs):
        print(f"Epoch {i+1}")
        train_one_epoch(model, data_loader, loss_fn, optimizer, device)
        print("----------------------------")
    print("Training is done.")


if __name__ == "__main__":
    # build model
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    print(f"using {device} device")

    # instantiating our dataset
    mel_spectrogram = torchaudio.transforms.MelSpectrogram(sample_rate=SAMPLE_RATE,
                                                           n_fft=1024,
                                                           hop_length=512,
                                                           n_mels=64)

    usd = UrbanSoundDataset(ANNOTATIONS_FILE,
                            AUDIO_DIR,
                            mel_spectrogram,
                            SAMPLE_RATE,
                            NUM_SAMPLES,
                            device)

    # create a data loader for the train set
    train_data_loader = DataLoader(usd, batch_size=BATCH_SIZE)


    vggnet = CNNNetwork().to(device)

    # instantiate loss function + optimizer
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(vggnet.parameters(),
                                 lr=LEARNING_RATE)

    # train model
    train(vggnet, train_data_loader, loss_fn,
          optimizer, device, EPOCHS)

    # save model
    torch.save(vggnet.state_dict(), "cnn_net.pth")
    print("model trained and stored at feedforward.pth")