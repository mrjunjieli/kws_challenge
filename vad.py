# -*- coding: utf-8 -*-


import collections
import contextlib
import sys
import os
import wave

import webrtcvad

AGGRESSIVENESS = 2

unprocess_file = []

def read_wave(path):
    """Reads wave file.

    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.

    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Args:
        frame_duration_ms: The desired frame duration in milliseconds.
        audio: The PCM data.
        sample_rate: The sample rate
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, vad, frames):
    """Filters out non-voiced audio frames.

    Args:
        sample_rate: The audio sample rate, in Hz.
        vad: An instance of webrtcvad.Vad.
        frames: A source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """

    voiced_frames = []
    for idx, frame in enumerate(frames):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            voiced_frames.append(frame)

    return b''.join([f.bytes for f in voiced_frames])


def voiced_frames_expand(voiced_frames, duration=2):
    total = duration * 8000 * 2
    expanded_voiced_frames = voiced_frames
    while len(expanded_voiced_frames) < total:
        expand_num = total - len(expanded_voiced_frames)
        expanded_voiced_frames += voiced_frames[:expand_num]

    return expanded_voiced_frames


def filter(wavdir, out_dir, expand=False):
    '''Apply vad with wave file.

    Args:
        wavpath: The input wave file.
        out_dir: The directory that contains the voiced audio.
        expand: Expand the frames or not, default False.
    '''
    print("wavpath:", wavdir)
    filenames = os.listdir(wavdir)
    for file in filenames: 
        main_name = file.split('.')[0]
        extension_name = file.split('.')[-1]
        if(extension_name!='wav' and extension_name!='mp3'):
            unprocess_file.append(file)
            continue
        wavpath = wavdir+'/'+file
        try:
            audio, sample_rate = read_wave(wavpath)
        except Exception as ex:
            print(ex)
            unprocess_file.append(file)
            continue
        # print('sample rate:%d'%sample_rate)
        vad = webrtcvad.Vad(AGGRESSIVENESS)
        frames = frame_generator(30, audio, sample_rate)
        frames = list(frames)
        voiced_frames = vad_collector(sample_rate, vad, frames)
        voiced_frames = voiced_frames_expand(voiced_frames, 2) if expand else voiced_frames
        # wav_name = wavpath.split('/')[-1]

        save_path = out_dir + '/' + main_name+'-clean.'+extension_name
       # print('-----save filename:',save_path)
        write_wave(save_path, voiced_frames, sample_rate)


def main():
    in_wav = '/Work19/2020/lijunjie/kws_challenge/KWS-Dev-Channel/'
    out_dir ='/Work19/2020/lijunjie/kws_challenge/KWS-Dev-Channel-Clean/'
    if(not (os.path.exists(out_dir))):
        os.makedirs(out_dir)
    filter(in_wav, out_dir, expand=False)
    if(list(unprocess_file)):
        print('unprocess files:')
        print(unprocess_file)
    # 你会在你out_dir目录下得到经过vad的test.wav文件


if __name__ == '__main__':
    main()
