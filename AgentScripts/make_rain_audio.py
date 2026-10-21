"""Original generated rain ambience. No third-party recordings."""
import math, random, array, wave, pathlib
root=pathlib.Path(__file__).resolve().parents[1];random.seed(24)
rate=22050;count=rate*20;values=array.array('h');low=0
for i in range(count):
    noise=random.uniform(-1,1);low=.965*low+.035*noise
    envelope=.83+.12*math.sin(2*math.pi*i/count*3)+.05*math.sin(2*math.pi*i/count*7)
    values.append(int(max(-1,min(1,(noise*.06+low*.65)*envelope))*24000))
folder=root/'ArtSource/Audio';folder.mkdir(exist_ok=True)
with wave.open(str(folder/'Rain_Interior_Loop.wav'),'wb') as out:
    out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate);out.writeframes(values.tobytes())
print('Original rain loop generated')
