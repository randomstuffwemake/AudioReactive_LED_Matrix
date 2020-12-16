# fftEqualizer - By: Sahil Rastogi - Sat Nov 21 2020

from Maix import GPIO
from Maix import I2S
from Maix import FFT
from fpioa_manager import fm
from modules import ws2812
import lcd, time, random


lcd.init(color=(0,0,255))
lcd.draw_string(lcd.width()//2-54,lcd.height()//2-4, "fftEqualizer", lcd.WHITE, lcd.BLUE)

ledPin, ledNum = 24, 150 #24 is digitalPin 5 of Maixduino

ws = ws2812(led_pin = ledPin, led_num = ledNum)

for i in range(ledNum):
    ws.set_led(i, (0, 0, 0))
ws.display()

fm.register(20, fm.fpioa.I2S0_IN_D0, force = True)
fm.register(19, fm.fpioa.I2S0_WS, force = True)
fm.register(18, fm.fpioa.I2S0_SCLK, force = True)
rx = I2S(I2S.DEVICE_0)
rx.channel_config(rx.CHANNEL_0, rx.RECEIVER, align_mode = I2S.STANDARD_MODE)
sampleRate = 38640
rx.set_sample_rate(sampleRate)
samplePoints = 1024
fftPoints = 128 # 64, 128, 256, 512
histNum = 10 # should ideally be equal to fftPoints
maxLedHeight = 15
maxHistHeight = 240

def mapValue(x, inMin, inMax, outMin, outMax):
    return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin

gammatable = [None] * 256

for i in range(256):
    x = i
    x /= 255
    x = pow(x, 2.5)
    x *= 255
    gammatable[i] = int(x)

color = [(gammatable[148], gammatable[0], gammatable[211]),
         (gammatable[75], gammatable[0], gammatable[130]),
         (gammatable[0], gammatable[0], gammatable[255]),
         (gammatable[0], gammatable[255], gammatable[0]),
         (gammatable[150], gammatable[150], gammatable[0]),
         (gammatable[255], gammatable[127], gammatable[0]),
         (gammatable[255], gammatable[0], gammatable[0]),
         (gammatable[0], gammatable[127], gammatable[127])]

old = time.ticks_ms()
colorSelection = 0

while True:
    audio = rx.record(samplePoints)
    fftRes = FFT.run(audio.to_bytes(), fftPoints)
    fftAmp = FFT.amplitude(fftRes)
    new = time.ticks_ms()
    if new - old >= 500:
        colorSelection = random.randrange(8)
        old = new

    for i in range(histNum):
        if fftAmp[i] > maxHistHeight:
            histHeight = maxHistHeight
        else:
            histHeight = fftAmp[i]
        ledHeight = int(mapValue(histHeight, 0, maxHistHeight, 0, maxLedHeight))
        for j in range(maxLedHeight * i, (maxLedHeight * i) + ledHeight):
            ws.set_led(j, color[colorSelection])
        if(ledHeight != maxLedHeight):
            for j in range((maxLedHeight * i) + ledHeight, maxLedHeight * (i + 1)):
                ws.set_led(j, (0, 0, 0))

    ws.display()
