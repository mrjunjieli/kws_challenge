#!/bin/bash
# Created on 2018/12
# Author: Kaituo XU
# LastEditors: Junjie Li
# Conv-Tasnet for <<target speaker separation>>


export PATH=/Work18/2020/lijunjie/anaconda3/envs/torch1.1/bin:$PATH

#-------------------------------------------------------------------

data=/Work19/2020/lijunjie/kws_challenge/Data_for_TasNet/KWS     #the folder contains dataset 
stage=4 # Modify this to control to start from which stage

dumpdir=data  # directory to put generated json file includeing the map between TRAIN data and LABEL data

# -- START Conv-TasNet Config
train_dir=$dumpdir/train
valid_dir=$dumpdir/dev
evaluate_dir=$dumpdir/test
separate_dir=/Work19/2020/lijunjie/kws_challenge/KWS-Dev-Channel
sample_rate=8000
segment=-1  # seconds  if segment==-1 then containing the whole audio
cv_maxlen=-1  # seconds


#----------------------------------------------------------------------
# Network config
N=512
L=16
B=128
H=512
P=3
X=8
R=3
norm_type=gLN
causal=0
mask_nonlinear='relu'
C=1
# Training config
use_cuda=1
id=0
epochs=100
half_lr=1
early_stop=1
max_norm=5
pit=0
# minibatch
shuffle=1
batch_size=2
num_workers=4
# optimizer
optimizer=adam
lr=1e-3
momentum=0
l2=0
# save and visualize
checkpoint=0 
continue_from='/Work18/2020/lijunjie/kws_challenge/Conv-TasNet/egs/exp/train_r8000_N512_L16_B128_H512_P3_X8_R3_C1_gLN_causal0_relu_epoch100_half1_norm5_bs2_worker4_pit0_adam_lr1e-3_mmt0_l20_train/final.pth.tar'
print_freq=10
visdom=0
visdom_epoch=0
visdom_id="Conv-TasNet Training"
# evaluate
ev_use_cuda=1
cal_sdr=1
# -- END Conv-TasNet Config

# exp tag
#you can custom the folder containing the experiments logs etc.
tag="" # tag for managing experiments. 


# . utils/parse_options.sh || exit 1;
# . ./cmd.sh
# . ./path.sh

if [ $pit -le 0 ]; then 
  pit_command=''
else
  pit_command='--pit'
fi


if [ $stage -le 1 ]; then
  echo "Stage 1: Generating json files including wav path and duration"
  [ ! -d $dumpdir ] && mkdir $dumpdir
  # The foldr $data must to contain at least 3 folder named [train,dev,test]
  python ../src/preprocess.py --in-dir $data --out-dir $dumpdir --sample-rate $sample_rate
fi


if [ -z $tag ]; then
  expdir=exp/train_r${sample_rate}_N${N}_L${L}_B${B}_H${H}_P${P}_X${X}_R${R}_C${C}_${norm_type}_causal${causal}_${mask_nonlinear}_epoch${epochs}_half${half_lr}_norm${max_norm}_bs${batch_size}_worker${num_workers}_pit${pit}_${optimizer}_lr${lr}_mmt${momentum}_l2${l2}_`basename $train_dir`
else
  expdir=exp/train_${tag}
fi

if [ $stage -le 2 ]; then
  echo "Stage 2: Training"
  echo "pit"
  echo $pit
  # ${cuda_cmd} --gpu ${ngpu} ${expdir}/train.log \
  [ ! -d ${expdir}/train.log ] && mkdir ${expdir}
    CUDA_VISIBLE_DEVICES="$id" \
    python ../src/train.py \
    --train_dir $valid_dir \
    --valid_dir $valid_dir \
    --sample_rate $sample_rate \
    --segment $segment \
    --cv_maxlen $cv_maxlen \
    --N $N \
    --L $L \
    --B $B \
    --H $H \
    --P $P \
    --X $X \
    --R $R \
    --C $C \
    --norm_type $norm_type \
    --causal $causal \
    --mask_nonlinear $mask_nonlinear \
    --use_cuda $use_cuda \
    --epochs $epochs \
    --half_lr $half_lr \
    --early_stop $early_stop \
    --max_norm $max_norm \
    --shuffle $shuffle \
    --batch_size $batch_size \
    --num_workers $num_workers \
    --optimizer $optimizer \
    --lr $lr \
    --momentum $momentum \
    --l2 $l2 \
    --save_folder ${expdir} \
    --checkpoint $checkpoint \
    --continue_from "$continue_from" \
    --print_freq ${print_freq} \
    --visdom $visdom \
    --visdom_epoch $visdom_epoch \
    --visdom_id "$visdom_id" \
    $pit_command > ${expdir}/train.log 
fi


if [ $stage -le 3 ]; then
  echo "Stage 3: Evaluate separation performance"
  # ${decode_cmd} --gpu ${ngpu} ${expdir}/evaluate.log \
    python ../src/evaluate.py \
    --model_path ${expdir}/final.pth.tar \
    --data_dir $evaluate_dir \
    --cal_sdr $cal_sdr \
    --use_cuda $ev_use_cuda \
    --sample_rate $sample_rate \
    --batch_size $batch_size \
    $pit_command > ${expdir}/evaluate.log 
fi


if [ $stage -le 4 ]; then
  echo "Stage 4: Separate speech using Conv-TasNet"
if [ -z $tag ]; then
  separate_out_dir=/Work19/2020/lijunjie/kws_challenge/OutData_of_TasNet/train_r${sample_rate}_N${N}_L${L}_B${B}_H${H}_P${P}_X${X}_R${R}_C${C}_${norm_type}_causal${causal}_${mask_nonlinear}_epoch${epochs}_half${half_lr}_norm${max_norm}_bs${batch_size}_worker${num_workers}_pit${pit}_${optimizer}_lr${lr}_mmt${momentum}_l2${l2}_`basename $train_dir`
else
  separate_out_dir=/Work19/2020/lijunjie/kws_challenge/OutData_of_TasNet/train_${tag}
fi
  # ${decode_cmd} --gpu ${ngpu} ${separate_out_dir}/separate.log \
    python ../src/separate.py \
    --model_path ${expdir}/final.pth.tar \
    --mix_dir $separate_dir \
    --out_dir ${separate_out_dir} \
    --use_cuda $ev_use_cuda \
    --sample_rate $sample_rate \
    --batch_size $batch_size > ${expdir}/separate.log
fi
