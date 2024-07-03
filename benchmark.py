#!/usr/bin/env python3
import os
import re
import csv
import sys
import subprocess



# Define your commands
commands = {
    "HF-TRT": "python3 $MODEL_PATH/../convert_checkpoint.py --model_dir $MODEL_PATH/ --dtype float16 --output_dir $MODEL_PATH/trt_ckpt/",
    "HF-TRT-Quantized": "python3 $MODEL_PATH/../convert_checkpoint.py --model_dir $MODEL_PATH/ --dtype float16 --use_weight_only --output_dir $MODEL_PATH/trt_ckpt/quantized/",
    "TRT-engine": "trtllm-build --checkpoint_dir $MODEL_PATH/trt_ckpt/ --gemm_plugin float16 --output_dir $MODEL_PATH/trt_engines/",
    "TRT-engine-Quantized": "trtllm-build --checkpoint_dir $MODEL_PATH/trt_ckpt/quantized/ --gemm_plugin float16 --output_dir $MODEL_PATH/trt_engines/quantized/"
}

commands_benchmark = {
    "Hugging Face": "python3 $MODEL_PATH/../summarize.py --test_hf --hf_model_dir $MODEL_PATH/ --data_type fp16 --engine_dir $MODEL_PATH/trt_engines",
    "TensorRT-LLM": "python3 $MODEL_PATH/../summarize.py --test_trt_llm --hf_model_dir $MODEL_PATH/ --data_type fp16 --engine_dir $MODEL_PATH/trt_engines/",
    "TensorRT-LLM (INT8)": "python3 $MODEL_PATH/../summarize.py --test_trt_llm --hf_model_dir $MODEL_PATH/ --data_type fp16 --engine_dir $MODEL_PATH/trt_engines/quantized/"
}

# Choose the model you want to benchmark
# Argmunets from CLI : link to huggingface model


def convert_model_to_trt():
    keys = "HF-TRT"
    run_command(commands[keys])


def convert_model_to_trt_and_quantify():
    keys = "HF-TRT-Quantized"
    run_command(commands[keys])

def build_engine():
    keys = "TRT-engine"
    run_command(commands[keys])

def build_engine_quantized():
    keys = "TRT-engine-Quantized"
    run_command(commands[keys])


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def parse_output(output):
    # Extracting execution time
    time_match = re.search(r'real\s+(\d+)m([\d.]+)s', output)
    if time_match:
        minutes = int(time_match.group(1))
        seconds = float(time_match.group(2))
        exec_time = minutes * 60 + seconds
    else:
        exec_time = None
    
    rouge_scores = re.findall(r'rouge[12Lsum]+ : ([\d.]+)', output)
    rouge_scores = [float(score) for score in rouge_scores] if rouge_scores else []
    
    latency_match = re.search(r'total latency: ([\d.]+) sec', output)
    latency = float(latency_match.group(1)) if latency_match else None
    
    tokens_match = re.search(r'total output tokens: (\d+)', output)
    total_tokens = int(tokens_match.group(1)) if tokens_match else None
    
    tokens_per_sec_match = re.search(r'tokens per second: ([\d.]+)', output)
    tokens_per_sec = float(tokens_per_sec_match.group(1)) if tokens_per_sec_match else None
    
    return exec_time, rouge_scores, latency, total_tokens, tokens_per_sec

def benchmark_model():

    # Run commands and parse outputs
    results = {}
    for key, command in commands.items():
        output = run_command(command)
        results[key] = parse_output(output)


    # Prepare CSV data
    data = [
        ["Model", "Exec Time (s)", "ROUGE-1", "ROUGE-2", "ROUGE-L", "Latency (s)", "Total Tokens", "Tokens/s"],
        ["Hugging Face", results["Hugging Face"][0]] + results["Hugging Face"][1] + [None, None, None],
        ["TensorRT-LLM", results["TensorRT-LLM"][0]] + results["TensorRT-LLM"][1] + [results["TensorRT-LLM"][2], results["TensorRT-LLM"][3], results["TensorRT-LLM"][4]],
        ["TensorRT-LLM (INT8)", results["TensorRT-LLM (INT8)"][0]] + results["TensorRT-LLM (INT8)"][1] + [results["TensorRT-LLM (INT8)"][2], results["TensorRT-LLM (INT8)"][3], results["TensorRT-LLM (INT8)"][4]],
    ]

    # Write to CSV
    with open("output.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)



def helper():
    print("""
    Usage: benchmark.py <model name>
    Example: benchmark.py bloom-560m
    Model name is the one get after clone the model from huggingface (e.g. https://huggingface.co/bigscience/bloom-560m -> bloom-560m)

          """
          )

def main():
    if sys.argv[1] == "help" or len(sys.args) < 2:
        helper()
    else:
        model_name = sys.argv[1]
        MODEL_PATH = f"./model/{model_name}"
        os.environ['MODEL_PATH'] = MODEL_PATH
        convert_model_to_trt()
        convert_model_to_trt_and_quantify()
        build_engine()
        build_engine_quantized()
        benchmark_model()

if __name__ == "__main__":
    main()