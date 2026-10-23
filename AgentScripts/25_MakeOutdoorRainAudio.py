"""Original seamless stereo rain: broadband wash, low wind and irregular impacts."""
import random,math,array,wave,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
rate=32000;seconds=33;count=rate*seconds
channels=[]
for channel in range(2):
    rng=random.Random(240026+channel)
    data=array.array('f',[0])*count
    low=0.0;mid=0.0
    for i in range(count):
        n=rng.uniform(-1,1);low=.995*low+.005*n;mid=.84*mid+.16*n
        envelope=.88+.07*math.sin(2*math.pi*i/count*2)+.05*math.sin(2*math.pi*i/count*5+channel)
        data[i]=(n*.11+mid*.21+low*.65)*envelope
    for event in range(2400):
        start=rng.randrange(count);length=rng.randrange(100,1100);gain=rng.uniform(.015,.07)
        for k in range(length):
            data[(start+k)%count]+=rng.uniform(-1,1)*gain*math.exp(-k/(length*.16))
    overlap=rate
    for i in range(overlap):
        t=i/overlap;data[i]=data[i]*t+data[count-overlap+i]*(1-t)
    channels.append(data[:count-overlap])
output=array.array('h')
for i in range(len(channels[0])):
    for ch in channels:output.append(int(max(-.95,min(.95,ch[i]))*32767))
folder=root/'ArtSource/Audio';folder.mkdir(exist_ok=True)
with wave.open(str(folder/'Rain_District_Outdoor_Stereo.wav'),'wb') as wav:
    wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(output.tobytes())
print('Outdoor rain: 32 seconds, stereo, seamless crossfade, original synthesis')
