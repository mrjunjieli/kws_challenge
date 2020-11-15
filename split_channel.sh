input_dir="/CDShare/slt_kws_challenge_Mixture/KWS-Dev/"
output_dir="/Work19/2020/lijunjie/kws_challenge/KWS-Dev-Channel/"

[ ! -d $output_dir ] && mkdir $output_dir

index=0

for file in $(ls ${input_dir})
    do
	left_filename=${file%.*}
    sox ${input_dir}${file} ${output_dir}${left_filename}"_channel0.wav" remix 1
	let index++
    done
echo 'success process files:'
echo $index
