

# Conv-TasNet
These files are modified according to  
This Conv-TasNet model has been modified to **target speaker separation** .  

## Reference 
[Conv-Tesnet](https://github.com/nobel861017/Conv-TasNet)  
["TasNet: Surpassing Ideal Time-Frequency Masking for Speech Separation"](https://arxiv.org/abs/1809.07454).


## Usage
Before running, you need to have mixture and target audio data.  

### Workflow
Workflow of `egs/run.sh`:
- Stage 1: Generating json files including wav path and duration
- Stage 2: Training
- Stage 3: Evaluate separation performance
- Stage 4: Separate speech using Conv-TasNet

#### How to resume training?
```bash
$ bash run.sh --continue_from <model-path>
```
# vad.py
filter out the silence in the signal