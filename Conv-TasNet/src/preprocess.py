# Created on 2018/12
# Author: Kaituo XU
# LastEditor :Junjie Li
# LastEditTime: 2020/11

import argparse
import json
import os

import librosa


# def preprocess_one_dir(in_dir, out_dir, out_filename, sample_rate=8000):
#     file_infos = []
#     in_dir = os.path.abspath(in_dir)
#     wav_list = os.listdir(in_dir)
#     for wav_file in wav_list:
#         if not wav_file.endswith('.wav'):
#             continue
#         wav_path = os.path.join(in_dir, wav_file)
#         # samples, _ = librosa.load(wav_path, sr=sample_rate)
        
#         # file_infos.append((wav_path, len(samples)))
#         file_infos.append(wav_path)
#     if not os.path.exists(out_dir):
#         os.makedirs(out_dir)
#     with open(os.path.join(out_dir, out_filename + '.json'), 'w') as f:
#         json.dump(file_infos, f, indent=4)



def preprocess_mix_and_target(in_dir, out_dir,sample_rate=8000):
    #in_dir :the path of dataset containing at least three folders :train,dev,train
    #out_dir: the path of folder to generate mix-target json files
    # this function is to generate the map between mixdata and target data


    #the kws_challenge dataset 
    #the dataset folder train,dev,test should contain two folders:target and mix 
    target = os.path.join(in_dir,'target')
    mix = os.path.join(in_dir,'mix')
    
    target_files = os.listdir(target)
    target_files.sort()
    
    mix_files = os.listdir(mix)
    mix_files.sort()
    
    targetitem=[]
    targetkey=[]
    
    for file in target_files:
        key = file.split('.')[0]
        targetkey.append(key)
        targetitem.append(file)
    #generate a map filenamekey----filename
    #example file: abc.wav 
    #the map = [key:abc,values:abc.wav]
    targetdict = dict(zip(targetkey,targetitem))
     
    data = []
    for file in mix_files:
    #mix data name :key_*.wav
    #example:target file:abc.wav    
    #mix file:abc_noise2.wav
        key_ = file.split('_')[0]
        if(key_ in targetkey and file.endswith('.wav') and targetdict[key_].endswith('.wav')):
            mix_data,_ = librosa.load(os.path.join(in_dir+'/mix/',file),sample_rate)
            target_data,_ = librosa.load(os.path.join(in_dir+'/target/',targetdict[key_]),sample_rate)
            if(len(mix_data)==len(target_data)):
                data.append([os.path.join(in_dir+'/mix/',file),os.path.join(in_dir+'/target/',targetdict[key_])])
        else:
            print('no:',file)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not os.path.exists(out_dir+'/mix-target.json'):
        os.mknod(out_dir+'/mix-target.json')           
    with open(out_dir+'/mix-target.json','w') as f:
        json.dump(data,f)
#dict.json 
#example [['your mixdata path','your targetdata path'],[]...]



def preprocess(args):
    for data_type in ['train', 'dev','test']:
        preprocess_mix_and_target(os.path.join(args.in_dir,data_type),os.path.join(args.out_dir,data_type),args.sample_rate)



if __name__ == "__main__":
    parser = argparse.ArgumentParser("WSJ0 data preprocessing")
    parser.add_argument('--in-dir', type=str, default=None,
                        help='Directory path of wsj0 including tr, cv and tt')
    parser.add_argument('--out-dir', type=str, default=None,
                        help='Directory path to put output files')
    parser.add_argument('--sample-rate', type=int, default=8000,
                        help='Sample rate of audio file')
    args = parser.parse_args()
    print(args)
    preprocess(args)
