import os
import platform
import subprocess
import sys

def check_cuda():
    """
    Checks if CUDA version 11 is installed and adds /bin directory to path variable.

    Returns:
        True if CUDA is installed and added to path, False otherwise.
    """

    # Check if CUDA is installed
    if os.name == "nt":
        cuda_path = os.environ.get("CUDA_PATH", "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.0")
        if not os.path.exists(cuda_path):
            return False
    elif os.name == "posix":
        cuda_path = os.environ.get("CUDA_PATH", "/usr/local/cuda-11.0")
        if not os.path.exists(cuda_path):
            return False
    else:
        return False

    # Check if CUDA /bin directory is in path
    if "CUDA_PATH" in os.environ:
        cuda_bin_path = os.path.join(cuda_path, "bin")
        if cuda_bin_path not in os.environ["PATH"]:
            os.environ["PATH"] = os.pathsep.join([cuda_bin_path, os.environ["PATH"]])
    else:
        return False

    # Check if CUDA version is 11.X
    try:
        cuda_version = subprocess.check_output(["nvcc", "--version"]).decode("utf-8")
        if not cuda_version.startswith("nvcc: NVIDIA (R) Cuda compiler driver"):
            return False
        cuda_version = cuda_version.split(" ")[4]
        if not cuda_version.startswith("11."):
            return False
    except subprocess.CalledProcessError:
        return False

    return True


def check_cudnn():
    """
    Checks if CuDNN 8 for CUDA 11 is installed and adds /bin directory to path variable.

    Returns:
        True if CuDNN is installed and added to path, False otherwise.
    """

    # Check if CuDNN is installed
    if os.name == "nt":
        cudnn_path = os.environ.get("CUDNN_PATH", "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.0\\cudnn")
        if not os.path.exists(cudnn_path):
            return False
    elif os.name == "posix":
        cudnn_path = os.environ.get("CUDNN_PATH", "/usr/local/cuda-11.0/cudnn")
        if not os.path.exists(cudnn_path):
            return False
    else:
        return False

    # Check if CuDNN /bin directory is in path
    if "CUDNN_PATH" in os.environ:
        cudnn_bin_path = os.path.join(cudnn_path, "bin")
        if cudnn_bin_path not in os.environ["PATH"]:
            os.environ["PATH"] = os.pathsep.join([cudnn_bin_path, os.environ["PATH"]])
    else:
        return False

    # Check if CuDNN version is 8.X
    try:
        cudnn_version = subprocess.check_output(["cudnn-checker", "--version"]).decode("utf-8")
        if not cudnn_version.startswith("cuDNN"):
            return False
        cudnn_version = cudnn_version.split(" ")[1]
        if not cudnn_version.startswith("8."):
            return False
    except subprocess.CalledProcessError:
        return False

    return True
# Check both CUDA and cuDNN
if check_cuda() and check_cudnn():
    print("CUDA and cuDNN are installed correctly.")
else:
    print("CUDA 11 and/or cuDNN 8 for CUDA 11 are not installed correctly or paths for CUDA 11 and CuDNN 8 not configure. Please install them or change path. Links for instalation are: https://developer.nvidia.com/cuda-11-8-0-download-archive? and https://developer.nvidia.com/rdp/cudnn-archive")


#Conda environment creation
    
# Determine the operating system
operating_system = sys.platform

# Define the base name of the configuration file
base_name = "audio_sample_env.yml"

# Construct the path to the configuration file based on the operating system
if operating_system.startswith("win"):
    # If the operating system is Windows
    config_file = os.path.normcase(os.path.abspath(base_name))
elif operating_system.startswith("linux"):
    # If the operating system is Linux
    config_file = os.path.join(os.path.expanduser("~"), base_name)
elif operating_system.startswith("darwin"):
    # If the operating system is macOS
    config_file = os.path.join(os.path.expanduser("~"), base_name)
else:
    # If the operating system is not supported, display an error message
    print("Unsupported operating system.")
    sys.exit(1)



if platform.system() == "Windows":
    conda_command = f"conda env create --name audio_sample_env -f {config_file}"
elif platform.system() == "Darwin" or platform.system() == "Linux":
    conda_command = f"conda env create --name audio_sample_env -f {config_file}"

if platform.system() == "Windows":
    activation_command = ["conda", "activate", "audio_sample_env"]
elif platform.system() == "Darwin" or platform.system() == "Linux":
    activation_command = ["source", "activate", "audio_sample_env"]

subprocess.run(conda_command.split())
subprocess.run(activation_command, check=True, shell=True)