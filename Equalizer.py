import logging
import os 
import pandas as pd
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from tkinter import *
from tkinter import ttk
from scipy import signal
from PIL import ImageTk,Image
import librosa as lib
import pandas as pd
import ffmpeg
import librosa.display
from playsound import playsound
from os import path
from pydub import AudioSegment
from matplotlib import animation
import time
import IPython.display as ipd
import sounddevice as sd
import soundfile as sf
from threading import Thread
logging.basicConfig(filename="Equalizer Logger.log", level=logging.DEBUG,format='%(asctime)s:%(funcName)s:%(message)s')
logging.getLogger('matplotlib.font_manager').disabled = True
global AmplitudeForEqualiser
global samplerate
global timeofmusic
global originalamplitude
global originaltimeofmusic
global musicani
global signal_fig
global FrequencySpectrumFlag
FrequencySpectrumFlag=1
MusicIndex=0
sd.default.latency = 'low'
playpausetoggle=0

def ChangeInstrument(self):
    BongoFrame.pack_forget()
    PfluteFrame.pack_forget()
    XyloFrame.pack_forget()
    Instrument=CB.get()
    CB['values'] = ["Bongo","Pan Flute","Xylophone"]
    logging.debug(Instrument)
    if Instrument == "Bongo":
        BongoFrame.pack(pady=40)
    elif Instrument == "Pan Flute":
        PfluteFrame.pack(padx=200,pady=40)
    elif Instrument == "Xylophone":
        XyloFrame.pack(padx=45,pady=40)
        
def StopSound(self):
    pass

def Pflute(button):
    logging.debug(button)
    strength=1/StrengthSlider.get()
    Pflutetime= np.linspace(0,5,5*7000)
    PfluteFreq= [1567.98,1479.98,1318.51,1174.66,1046.5,987.77,880,783.99,739.99,659.25,587.33,523.25]
    NoiseFreq1=[3150,  3950 ,600,2350,2075,1975,1750,1575,1475,1325,1775,1575]
    NoiseMagnitude1=[0.025,0.0158,0.01,0.04167,0.0458,0.0333,0.0167,0.018,0.032,0.025,0.114,0.1923]
    NoiseFreq2=[0,0,2600,0,3150,2950,2650,2350,2200,2000,2950,2600]
    NoiseMagnitude2=[0,0,0.03,0,0.1,0.0667,0.05,0.12,0.1935,0.092,0.0381,0.0538]
    MainComponent=np.sin(PfluteFreq[button-1]*2*np.pi*Pflutetime)
    NoiseComponent1=NoiseMagnitude1[button-1]*np.sin(NoiseFreq1[button-1]*2*np.pi*Pflutetime)
    NoiseComponent2=NoiseMagnitude2[button-1]*np.sin(NoiseFreq2[button-1]*2*np.pi*Pflutetime)
    logging.debug(NoiseMagnitude1[button-1])
    logging.debug(NoiseMagnitude2[button-1])
    logging.debug(NoiseFreq1[button-1])
    logging.debug(NoiseFreq2[button-1])
    PfluteWave=np.multiply(MainComponent+NoiseComponent1+NoiseComponent2,np.exp(-0.6*Pflutetime))
    sd.play(strength*PfluteWave,7000)

def Bongo(button):
    strength=1/StrengthSlider.get()
    BongoTime = np.linspace(0,10,1001)
    DampingFactor = 0.4
    BongoMag = 2*button
    BongoFreq = 0.9 - (button-1)*(0.4)
    BongoWave = np.exp(-1*DampingFactor*BongoTime) * BongoMag * np.sin(button*BongoFreq * BongoTime * np.pi)
    sd.play(strength*BongoWave)
    
def xylo(button):
    strength=1/StrengthSlider.get()
    xylotime= np.linspace(0,3,int(3*4500))
    xylofreq=1050 + (button-1)*150
    xylosound= np.multiply(np.sin(xylofreq*2*np.pi*xylotime),np.exp(-5*xylotime))
    sd.play(strength*xylosound,4500)

def openFile():
    global AmplitudeForEqualiser
    global timeofmusic
    global originalamplitude
    global originaltimeofmusic
    global samplerate
    global signal_fig
    global signal_graph
    signal_graph.clear()
    filepath = filedialog.askopenfilename(filetypes= (("wav files",".WAV"),("all files",".*")))
    openFile.filepath = filepath
    file = open(filepath,'r')
    AmplitudeForEqualiser, samplerate = librosa.load(filepath)
    open_button.pack_forget()
    sd.play(AmplitudeForEqualiser,samplerate)
    timeofmusic = np.linspace(0, len(AmplitudeForEqualiser) / samplerate, num=len(AmplitudeForEqualiser))
    originalamplitude=AmplitudeForEqualiser
    originaltimeofmusic=timeofmusic
    global PointsPerInterval
    PointsPerInterval=int(0.1*len(timeofmusic)/max(timeofmusic))
    global MusicSliderf
    def MusicSliderf(self):
        global AmplitudeForEqualiser
        if abs(getPos()-MusicIndex) > PointsPerInterval:
            if(playpausetoggle ==0):
                sd.play(AmplitudeForEqualiser[getPos():],samplerate)
    MusicSlider=Scale(MusicSliderFrame,from_=0,to =len(timeofmusic)-2,orient =HORIZONTAL,showvalue=0,command=MusicSliderf,bg='white',highlightbackground='white')
    MusicSlider.pack(side = TOP,fill ='x',expand= True,padx=200)
    file.close()
    signal_graph.set_ylim([2*min(originalamplitude),2*max(originalamplitude)])
    signal_graph.plot(timeofmusic, AmplitudeForEqualiser)
    signal_fig.canvas.draw_idle()
    spec()
    global getPos
    global setPos
    def getPos():
        return MusicSlider.get()
    def setPos(start):
        global AmplitudeForEqualiser
        sd.play(AmplitudeForEqualiser[start:],samplerate)
    global animate
    def animate(i):
        global PointsPerInterval
        global MusicIndex  
        MusicIndex=MusicSlider.get()
        signal_graph.set_xlim(timeofmusic[MusicIndex],timeofmusic[MusicIndex+PointsPerInterval]) 
        if playpausetoggle == 0:
            MusicIndex+=PointsPerInterval
        if MusicIndex>=len(timeofmusic)-PointsPerInterval:
            MusicIndex=0
            sd.play(AmplitudeForEqualiser,samplerate)
        MusicSlider.set(MusicIndex)   

        if MusicSlider.get()>=len(timeofmusic)-101:
            MusicSlider.set(0)
    global musicani
    animate(0)
    musicani=animation.FuncAnimation(signal_fig, animate,interval=100,blit=False)
  
def Fourier(Time,Signal_t):
    fourierTransform = np.fft.fft(Signal_t)/len(Signal_t)# Normalize amplitude
    fourierTransform = fourierTransform[range(int(len(Signal_t)))] # Exclude sampling frequency 
    pointsCount     = len(Signal_t)
    values      = np.arange(int(pointsCount))
    timeperiod=max(Time)
    timestep=Time[1]-Time[0]
    Signal_wj=fourierTransform*timeperiod/timestep
    frequencies=values/timeperiod
    return frequencies,Signal_wj

def InverseFourier(Frequency,Signal_wj):
    Signal_t = np.fft.ifft(Signal_wj)
    T=1/(Frequency[1]-Frequency[0])
    Signal_t=np.real(Signal_t)
    time= np.linspace(0,T,len(Signal_t))
    return time,Signal_t

def UnitStep(Magnitude,Shift,Time):
    UnitStep=[]
    TimeStep= Time[1]-Time[0]
    Start = Shift/TimeStep
    End= len(Time)
    
    for i in range (0,End):
        if i<Start:
            UnitStep.append(0)
        else:  
            UnitStep.append(Magnitude)
    return UnitStep

def Amplify(Frequency,Signal_wj,AmplificationFactor,MinFreq,MaxFreq): 
    AmplificationSignal= np.subtract(np.add(UnitStep(1,0,Frequency),UnitStep(AmplificationFactor,MinFreq,Frequency)),UnitStep(AmplificationFactor,MaxFreq,Frequency))
    AmplifiedSignal=np.multiply(AmplificationSignal,Signal_wj)
    return Frequency,AmplifiedSignal

def Attenuate(Frequency,Signal_wj,AttenuationFactor,MinFreq,MaxFreq):
    Frequency,AmplifiedSignal=Amplify(Frequency,Signal_wj,(-1)*AttenuationFactor,MinFreq,MaxFreq)
    return Frequency,AmplifiedSignal

def spec():
    global AmplitudeForEqualiser
    specto_graph.clear()
    specto_graph.plot = specto_graph.specgram(AmplitudeForEqualiser,samplerate)  
    specto_fig.canvas.draw_idle()

def PlayPause():
    global pausePos
    global playpausetoggle
    global AmplitudeForEqualiser
    if playpausetoggle ==0:
        sd.play(AmplitudeForEqualiser[0:1],samplerate)
    else:
        sd.play(AmplitudeForEqualiser[getPos():],samplerate)
    playpausetoggle+=1
    if playpausetoggle==2:
        playpausetoggle=0
        
def Equalise(self):
    global samplerate
    global AmplitudeForEqualiser
    global InstrumentsSliders
    global GuitarIndex
    global XyloIndex
    global PianoIndex
    global SaxoIndex
    global DrumsIndex
    SliderVolumeFlag=0
    sd.play(AmplitudeForEqualiser[0:1],samplerate)
    Volume= volume_slider.get()  
    GuitarIndex=0
    XyloIndex=1
    PianoIndex=2
    SaxoIndex=3
    DrumsIndex=4
    MinFreqArr=[80,1000,0,0,2150]
    MaxFreqArr=[630,2150,2150,1000,12000]
    InstrumentsVolumesArray= [0,0,0,0,0]
    for InstrumentsCounter in range (0,5):
        InstrumentsVolumesArray[InstrumentsCounter]= InstrumentsSliders[InstrumentsCounter].get()/10
    TimeForEqualiser= originaltimeofmusic
    AmplitudeForEqualiser=Volume*originalamplitude
    for SliderFlagCounter in range (0,5):
        if (InstrumentsVolumesArray[SliderFlagCounter]!=0):
            SliderVolumeFlag=1
    #fourier
    if (SliderVolumeFlag==1):
        musicfreq,amplitude_wj=Fourier(TimeForEqualiser,AmplitudeForEqualiser)
        MaxFreq=max(musicfreq)
    #amplify
    for AmplifyingCounter in range (0,5):  
        if (InstrumentsVolumesArray[AmplifyingCounter] !=0):
            musicfreq,amplitude_wj=Amplify(musicfreq,amplitude_wj,InstrumentsVolumesArray[AmplifyingCounter],MinFreqArr[AmplifyingCounter],MaxFreqArr[AmplifyingCounter])
            musicfreq,amplitude_wj=Attenuate(musicfreq,amplitude_wj,InstrumentsVolumesArray[AmplifyingCounter],MaxFreq-MinFreqArr[AmplifyingCounter],MaxFreq-MaxFreqArr[AmplifyingCounter])
    #inverse fourier
    if (SliderVolumeFlag==1):
        TimeForEqualiser,AmplitudeForEqualiser=InverseFourier(musicfreq,amplitude_wj)   
    #Frequency Spectrum
    if FrequencySpectrumFlag ==1:
        FrequencySpectrumfreq,FrequencySpectrumamp=Fourier(originaltimeofmusic,originalamplitude)
        FrequencySpectrumAx_Ymax=2*max(abs(FrequencySpectrumamp))
        FrequencySpectrumAx_Xmax=0.5*max(FrequencySpectrumfreq)
        FrequencySpectrumAx.clear()
        FrequencySpectrumAx.grid()
        FrequencySpectrumAx.set_ylim(0,FrequencySpectrumAx_Ymax)
        FrequencySpectrumAx.set_xlim(-100,FrequencySpectrumAx_Xmax)
        if (SliderVolumeFlag==1):
            FrequencySpectrumAx.plot(musicfreq,abs(amplitude_wj))
        else:
            FrequencySpectrumAx.plot(FrequencySpectrumfreq,Volume*abs(FrequencySpectrumamp))
        FrequencySpectrumFig.canvas.draw_idle()    
    minX,maxX= signal_graph.get_xlim()
    signal_graph.clear()
    signal_graph.set_xlim([minX,maxX])
    signal_graph.set_ylim([2*min(originalamplitude),2*max(originalamplitude)])
    signal_graph.plot(TimeForEqualiser, AmplitudeForEqualiser)
    signal_fig.canvas.draw_idle()
    if(playpausetoggle ==0):
        sd.play(AmplitudeForEqualiser[getPos():],samplerate)
    spec()


# =======================GUI=======================    
root = tk.Tk()
root.geometry("920x780")
TabStyle = ttk.Style()
TabStyle.configure('My.TButton', foreground = 'white')
TabStyle.configure('My.TFrame', background = 'white',foreground = 'white')
tabControl = ttk.Notebook(root)  
main_tab = ttk.Frame(tabControl)
music_generator_tab = ttk.Frame(tabControl,style = 'My.TFrame')
tabControl.add(main_tab, text ='equalizer')
tabControl.add(music_generator_tab, text ='music generator')
tabControl.pack(expand = True, fill ="both")
#======================= Equalizer Toolbox =======================
buttons_frame = tk.Frame(main_tab)
buttons_frame.pack(side=TOP,expand =True,fill ='both')
open_button = tk.Button(buttons_frame,text ='open',command=openFile)
playpause_button = tk.Button(buttons_frame,text = 'play/pause',command=PlayPause)
volume_slider = Scale(buttons_frame,from_=0,to =1,orient =HORIZONTAL,resolution=0.1,showvalue=0)
volume_slider.set(1)
volume_slider.bind("<ButtonRelease-1>",Equalise)
open_button.pack(side =LEFT,fill ='x')
playpause_button.pack(side = LEFT,fill ='x')
volume_slider.pack(side = LEFT)

#======================= Plots =======================
graph_frame = tk.Frame(main_tab)
graph_frame.pack(side=TOP,expand =True,fill ='both')
signal_fig,(signal_graph)=plt.subplots(1)
GraphCanvas = FigureCanvasTkAgg(signal_fig,master =graph_frame)             
GraphCanvas.get_tk_widget().pack(fill = 'both',expand =True)

MusicSliderFrame=tk.Frame(main_tab,bg='white')
MusicSliderFrame.pack(side=TOP,expand =True,fill ='both')


spectrogram_frame = tk.Frame(main_tab)
spectrogram_frame.pack(side=TOP,expand =True,fill ='both')
specto_fig,(specto_graph)=plt.subplots(1)
SpectroCanvas = FigureCanvasTkAgg(specto_fig,master =spectrogram_frame)                      
SpectroCanvas.get_tk_widget().pack(fill = 'both',expand =True,side=LEFT)                
SpectroCanvas.get_tk_widget().pack(fill = 'both',expand =True)

if (FrequencySpectrumFlag==1):
    FrequencySpectrumFig,(FrequencySpectrumAx)=plt.subplots(1)
    FrequencySpectrumCanvas = FigureCanvasTkAgg(FrequencySpectrumFig,master =spectrogram_frame)        
    FrequencySpectrumCanvas.get_tk_widget().pack(fill = 'both',expand =True,side=RIGHT)
#======================= Equalizer Sliders =======================
sliders_frame = tk.Frame(main_tab)
sliders_frame.pack(side=TOP,expand =True,fill ='both')
guitar_frame = tk.Frame(sliders_frame)
guitar_frame.pack(side = LEFT,expand =True,fill ='both')
guitar_img = Image.open("Screenshot_7.png")  
resized_guitar = guitar_img.resize((25,25),Image.ANTIALIAS)
guitar_resized_image = ImageTk.PhotoImage(resized_guitar)
guitar_icon = tk.Label(guitar_frame,image = guitar_resized_image)
InstrumentsSliders=[]
InstrumentsSliders.append(Scale(guitar_frame,from_=50,to =-10,orient =VERTICAL,resolution=1))
GuitarIndex=0
InstrumentsSliders[GuitarIndex].bind("<ButtonRelease-1>",Equalise)
guitar_label = tk.Label(guitar_frame, text = 'Guitar')
guitar_label.pack()
guitar_icon.pack() 
InstrumentsSliders[GuitarIndex].pack()

xylo_frame =tk.Frame(sliders_frame)
xylo_frame.pack(side = LEFT,expand =True,fill ='both')
xylo_img = Image.open("Screenshot_2.png")  
resized_xylo = xylo_img.resize((25,25),Image.ANTIALIAS)
xylo_resized_image = ImageTk.PhotoImage(resized_xylo)
xylo_icon = tk.Label(xylo_frame,image = xylo_resized_image)
InstrumentsSliders.append(Scale(xylo_frame,from_=50,to =-10,orient =VERTICAL,resolution=1))
XyloIndex=1
InstrumentsSliders[XyloIndex].bind("<ButtonRelease-1>",Equalise)
xylo_label = tk.Label(xylo_frame,text ='xylophone')
xylo_label.pack()
xylo_icon.pack()
InstrumentsSliders[XyloIndex].pack()

piano_frame =tk.Frame(sliders_frame)
piano_frame.pack(side =LEFT,expand =True,fill ='both')
piano_img = Image.open("Screenshot_3.png")  
resized_piano = piano_img.resize((25,25),Image.ANTIALIAS)
piano_resized_image = ImageTk.PhotoImage(resized_piano)
piano_icon = tk.Label(piano_frame,image = piano_resized_image)
InstrumentsSliders.append(Scale(piano_frame,from_=50,to =-10,orient =VERTICAL,resolution=1))
PianoIndex=2
InstrumentsSliders[PianoIndex].bind("<ButtonRelease-1>",Equalise)
piano_label =tk.Label(piano_frame,text="piano")
piano_label.pack()
piano_icon.pack()
InstrumentsSliders[PianoIndex].pack()

saxphone_frame= tk.Frame(sliders_frame)
saxphone_frame.pack(side= LEFT,expand =True,fill ='both')
saxphone_img = Image.open("Screenshot_4.png")  
resized_saxphone = saxphone_img.resize((25,25),Image.ANTIALIAS)
saxphone_resized_image = ImageTk.PhotoImage(resized_saxphone)
saxphone_icon = tk.Label(saxphone_frame,image = saxphone_resized_image)
InstrumentsSliders.append(Scale(saxphone_frame,from_=50,to =-10,orient =VERTICAL,resolution=1))
SaxoIndex=3
InstrumentsSliders[SaxoIndex].bind("<ButtonRelease-1>",Equalise)
saxphone_label =tk.Label(saxphone_frame,text = 'saxophone')
saxphone_label.pack()
saxphone_icon.pack()
InstrumentsSliders[SaxoIndex].pack() 

drums_frame = tk.Frame(sliders_frame)
drums_frame.pack(side = LEFT,expand =True,fill ='both')
drums_img = Image.open("Screenshot_1.png")  
resized_drums = drums_img.resize((25,25),Image.ANTIALIAS)
drums_resized_image = ImageTk.PhotoImage(resized_drums)
drums_icon = tk.Label(drums_frame,image = drums_resized_image)
InstrumentsSliders.append(Scale(drums_frame,from_=50,to =-10,orient =VERTICAL,resolution=1))
DrumsIndex=4
InstrumentsSliders[DrumsIndex].bind("<ButtonRelease-1>",Equalise)
drums_label = tk.Label(drums_frame, text = 'drums')
drums_label.pack()
drums_icon.pack()
InstrumentsSliders[DrumsIndex].pack()
#======================= Instruments Control =======================
CBframe = tk.Frame(music_generator_tab)
CBframe.pack(side =TOP,fill='x')
CB=ttk.Combobox(CBframe)
CB['values'] = ["Choose Instrument..","Bongo","Pan Flute","Xylophone"]
CB.current(0)
CB.pack(side = LEFT,fill ='x',padx=15)
CB.bind("<<ComboboxSelected>>", ChangeInstrument)
StrengthSlider= Scale(CBframe,from_=1,to =10,orient =HORIZONTAL,resolution=1,showvalue=0,label="      +Power-")
StrengthSlider.set(1)
StrengthSlider.pack(side = LEFT,fill ='x')
#======================= Bongo =======================
BongoFrame = tk.Frame(music_generator_tab,bg='white')
Bongo1 = ImageTk.PhotoImage(file="Bongo1.png")
BongoBt1=tk.Button(BongoFrame,image=Bongo1,highlightthickness = 0, bd = 0,command =lambda:Bongo(1))
BongoBt1.grid(row=0,column=0,pady=100)
Bongo2 = ImageTk.PhotoImage(file="Bongo2.png")
BongoBt2=tk.Button(BongoFrame,image=Bongo2,highlightthickness = 0, bd = 0,command =lambda:Bongo(2))
BongoBt2.grid(row=0,column=1,padx=0)
#======================= Pan Flute =======================
PfluteFrame = tk.Frame(music_generator_tab,bg='white')
Pflute1 = ImageTk.PhotoImage(file="pflute1.png")
Pflute1Bt=tk.Button(PfluteFrame,image=Pflute1,highlightthickness = 0, bd = 0)
Pflute1Bt.bind('<ButtonPress-1>',lambda self:Pflute(1))
Pflute1Bt.bind('<ButtonRelease-1>',StopSound)
Pflute1Bt.grid(row=0,column=11)
Pflute2 = ImageTk.PhotoImage(file="pflute2.png")
Pflute2Bt=tk.Button(PfluteFrame,image=Pflute2,highlightthickness = 0, bd = 0)
Pflute2Bt.bind('<ButtonPress-1>',lambda self:Pflute(2))
Pflute2Bt.bind('<ButtonRelease-1>',StopSound)
Pflute2Bt.grid(row=0,column=10)
Pflute3 = ImageTk.PhotoImage(file="pflute3.png")
Pflute3Bt=tk.Button(PfluteFrame,image=Pflute3,highlightthickness = 0, bd = 0)
Pflute3Bt.bind('<ButtonPress-1>',lambda self:Pflute(3))
Pflute3Bt.bind('<ButtonRelease-1>',StopSound)
Pflute3Bt.grid(row=0,column=9)
Pflute4 = ImageTk.PhotoImage(file="pflute4.png")
Pflute4Bt=tk.Button(PfluteFrame,image=Pflute4,highlightthickness = 0, bd = 0)
Pflute4Bt.bind('<ButtonPress-1>',lambda self:Pflute(4))
Pflute4Bt.bind('<ButtonRelease-1>',StopSound)
Pflute4Bt.grid(row=0,column=8)
Pflute5 = ImageTk.PhotoImage(file="pflute5.png")
Pflute5Bt=tk.Button(PfluteFrame,image=Pflute5,highlightthickness = 0, bd = 0)
Pflute5Bt.bind('<ButtonPress-1>',lambda self:Pflute(5))
Pflute5Bt.bind('<ButtonRelease-1>',StopSound)
Pflute5Bt.grid(row=0,column=7)
Pflute6 = ImageTk.PhotoImage(file="pflute6.png")
Pflute6Bt=tk.Button(PfluteFrame,image=Pflute6,highlightthickness = 0, bd = 0)
Pflute6Bt.bind('<ButtonPress-1>',lambda self:Pflute(6))
Pflute6Bt.bind('<ButtonRelease-1>',StopSound)
Pflute6Bt.grid(row=0,column=6)
Pflute7 = ImageTk.PhotoImage(file="pflute7.png")
Pflute7Bt=tk.Button(PfluteFrame,image=Pflute7,highlightthickness = 0, bd = 0)
Pflute7Bt.bind('<ButtonPress-1>',lambda self:Pflute(7))
Pflute7Bt.bind('<ButtonRelease-1>',StopSound)
Pflute7Bt.grid(row=0,column=5)
Pflute8 = ImageTk.PhotoImage(file="pflute8.png")
Pflute8Bt=tk.Button(PfluteFrame,image=Pflute8,highlightthickness = 0, bd = 0)
Pflute8Bt.bind('<ButtonPress-1>',lambda self:Pflute(8))
Pflute8Bt.bind('<ButtonRelease-1>',StopSound)
Pflute8Bt.grid(row=0,column=4)
Pflute9 = ImageTk.PhotoImage(file="pflute9.png")
Pflute9Bt=tk.Button(PfluteFrame,image=Pflute9,highlightthickness = 0, bd = 0)
Pflute9Bt.bind('<ButtonPress-1>',lambda self:Pflute(9))
Pflute9Bt.bind('<ButtonRelease-1>',StopSound)
Pflute9Bt.grid(row=0,column=3)
Pflute10 = ImageTk.PhotoImage(file="pflute10.png")
Pflute10Bt=tk.Button(PfluteFrame,image=Pflute10,highlightthickness = 0, bd = 0)
Pflute10Bt.bind('<ButtonPress-1>',lambda self:Pflute(10))
Pflute10Bt.bind('<ButtonRelease-1>',StopSound)
Pflute10Bt.grid(row=0,column=2)
Pflute11 = ImageTk.PhotoImage(file="pflute11.png")
Pflute11Bt=tk.Button(PfluteFrame,image=Pflute11,highlightthickness = 0, bd = 0)
Pflute11Bt.bind('<ButtonPress-1>',lambda self:Pflute(11))
Pflute11Bt.bind('<ButtonRelease-1>',StopSound)
Pflute11Bt.grid(row=0,column=1)
Pflute12 = ImageTk.PhotoImage(file="pflute12.png")
Pflute12Bt=tk.Button(PfluteFrame,image=Pflute12,highlightthickness = 0, bd = 0)
Pflute12Bt.bind('<ButtonPress-1>',lambda self:Pflute(12))
Pflute12Bt.bind('<ButtonRelease-1>',StopSound)
Pflute12Bt.grid(row=0,column=0)
# ======================= xylophone =======================
XyloFrame = tk.Frame(music_generator_tab,bg='white')
Xylo1 = ImageTk.PhotoImage(file="Xylophone1.png")
XyloBt1=tk.Button(XyloFrame,image=Xylo1,command =lambda:xylo(1))
XyloBt1.pack(side=LEFT)
Xylo2 = ImageTk.PhotoImage(file="Xylophone2.png")
XyloBt2=tk.Button(XyloFrame,image=Xylo2,command =lambda:xylo(2))
XyloBt2.pack(side=LEFT)
Xylo3 = ImageTk.PhotoImage(file="Xylophone3.png")
XyloBt3=tk.Button(XyloFrame,image=Xylo3,command =lambda:xylo(3))
XyloBt3.pack(side=LEFT)
Xylo4 = ImageTk.PhotoImage(file="Xylophone4.png")
XyloBt4=tk.Button(XyloFrame,image=Xylo4,command =lambda:xylo(4))
XyloBt4.pack(side=LEFT)
Xylo5 = ImageTk.PhotoImage(file="Xylophone5.png")
XyloBt5=tk.Button(XyloFrame,image=Xylo5,command =lambda:xylo(5))
XyloBt5.pack(side=LEFT)
Xylo6 = ImageTk.PhotoImage(file="Xylophone6.png")
XyloBt6=tk.Button(XyloFrame,image=Xylo6,command =lambda:xylo(6))
XyloBt6.pack(side=LEFT)
Xylo7 = ImageTk.PhotoImage(file="Xylophone7.png")
XyloBt7=tk.Button(XyloFrame,image=Xylo7,command =lambda:xylo(7))
XyloBt7.pack(side=LEFT)
Xylo8 = ImageTk.PhotoImage(file="Xylophone8.png")
XyloBt8=tk.Button(XyloFrame,image=Xylo8,command =lambda:xylo(8))
XyloBt8.pack(side=LEFT)

root.mainloop()