import re # remove all non-alphabet characters
import argparse # needed for CLI applications to have arguments(e.g: python3 main.py -h/-l/-m/...)
import queue
import sys
import sounddevice as sd
import vosk

model = vosk.Model(lang="en-us")
rate = 44100 # sample rate in kHz
audio_device = 0

q = queue.Queue()  # queue = linear data structure that follows the First In First Out (FIFO) rule

print(sd.query_devices())

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# listen to audio device(with specified parameters)
with sd.RawInputStream(samplerate=rate, blocksize = 8000, device=audio_device, dtype="int16", channels=1, callback=callback):
    print("#" * 80)
    print("Press Ctrl+C to stop the recording")
    print("#" * 80)
    
    finishWord = []
    wordBuffer = ""

    #capture the recognized text
    rec = vosk.KaldiRecognizer(model, rate)
    while True:
        data = q.get()

        # process the result. If the process of recognition is finished = return True
        if rec.AcceptWaveform(data):
            recordedText = rec.Result()
            print(recordedText)
            
            # remove everything before a column(:) character in a string
            resultText = recordedText.split(":", 1)[1]    
            
            # convert text(string) into lowercase
            resultText.casefold()
            # remove all non-alphabet characters ([^a-zA-Z] is a way to say all non-alphabet characters) 
            #resultText = re.sub(r'[^a-zA-Z]', '', resultText)
            resultText = re.sub(r'[""{}:,]', "", resultText)
            
            for character in resultText:
                if character != "\n":
                    wordBuffer += character
                    print(f"wordBuffer: {wordBuffer}")
                else:
                    wordBuffer = wordBuffer.strip()
                    finishWord.append(wordBuffer)
                    wordBuffer = ""
            
            print(f"FinishWord: {finishWord}")

            print(f"{resultText}")

        else:
            print(rec.PartialResult())
    