# Tensor-RTLLM
This project aim to convert/build/benchmark with tensor RT LLM huggingface model with only one command

## Pre require
```
# Obtain and start the basic docker image environment (optional).
docker run --rm --runtime=nvidia --gpus all --entrypoint /bin/bash -it nvidia/cuda:12.4.0-devel-ubuntu22.04
```
```
# Install dependencies, TensorRT-LLM requires Python 3.10
apt-get update && apt-get -y install python3.10 python3-pip openmpi-bin libopenmpi-dev git git-lfs

# Install the latest preview version (corresponding to the main branch) of TensorRT-LLM.
# If you want to install the stable version (corresponding to the release branch), please
# remove the `--pre` option.
pip3 install tensorrt_llm -U --pre --extra-index-url https://pypi.nvidia.com

# Check installation
python3 -c "import tensorrt_llm"
```
These steps are taken from the official Tensor RT-LLM installation guide: https://nvidia.github.io/TensorRT-LLM/installation/linux.html
```
# Get the source code required for running the example
git clone https://github.com/NVIDIA/TensorRT-LLM.git
cd TensorRT-LLM
git lfs install
```
This is from the quick start guide: https://nvidia.github.io/TensorRT-LLM/quick-start-guide.html

## Run the code

Now that everything is installed, I need to follow a specific architecture. 
```
mkdir model
cd model
```

Go into the model directory, you can clone the huggingface model in it, once done you can go back to the parent directory by typing 
```
cd ..
```

And then you can clone this repository and run the following command 
Be sure that you have the right to execute the file 
```
./benchmark -m <model name> -hf <clone model name>
```
Model name correspond to the model name inside the folder exmaples of Tensor RT-LLM project 

## Example

An example with the model BigScience Large Open-science Open-access Multilingual Language Model Bloom-560m

```
mkdir model
cd model
git clone https://huggingface.co/bigscience/bloom-560m
cd ..
git clone https://github.com/engelsl/Tensor-RTLLM.git
cd Tensor-RTLLM
./benchmark -m bloom -hf bloom-560m
```






