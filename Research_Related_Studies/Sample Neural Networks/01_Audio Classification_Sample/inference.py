import torch
import torchaudio.transforms

from cnn import CNNNetwork
from urbansounddataset import UrbanSoundDataset
from train import AUDIO_DIR, ANNOTATIONS_FILE, SAMPLE_RATE, NUM_SAMPLES

class_mapping = [
    "air_conditioner",
    "car_horn",
    "children_playing",
    "dog_bark",
    "drilling",
    "engine_idling",
    "gun_shot",
    "jackhammer",
    "siren",
    "street_music"
]

def predict(model, input, target, class_mapping):
    model.eval()
    with torch.no_grad():
        predictions = model(input)
        predicted_index = predictions[0].argmax(0)
        predicted = class_mapping[predicted_index]
        expected = class_mapping[target]
    return predicted, expected

if __name__ == "__main__":
    # load back the model
    net = CNNNetwork()
    state_dict = torch.load("cnn_net.pth")
    net.load_state_dict(state_dict)

    # load urban sound dataset
    mel_spectrogram = torchaudio.transforms.MelSpectrogram(
        sample_rate=SAMPLE_RATE,
        n_fft=1024,
        hop_length=512,
        n_mels=64
    )

    usd = UrbanSoundDataset (ANNOTATIONS_FILE,
                             AUDIO_DIR,
                             mel_spectrogram,
                             SAMPLE_RATE,
                             NUM_SAMPLES,
                             "cpu")
    '''
    get a sample from the urbansound dataset for inference
    usd is a tensor that has 3 dimensions
    [num_channels, frequency axis, time axis]
    but pytorch requires 4 dimensions
    so we need to insert an extra dimension in the 3-dimensional input
    '''
    for i in range(20):
        input, target = usd[i][0], usd[i][1]
        input.unsqueeze_(0)
        # make an inference
        predicted, expected = predict(net, input, target, class_mapping)
        print(f"Predicted: f'{predicted}', expected: '{expected}'")

