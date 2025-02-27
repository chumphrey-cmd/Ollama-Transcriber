# Purpose

This project offers a privacy-focused solution for transcribing and summarizing audio recordings through entirely local processing. Using OpenAI's Whisper for transcription and local LLMs via Ollama for summarization, it processes audio files (**MP3/WAV**) entirely on your machine, ensuring sensitive content never leaves your environment.

The tool automatically generates structured summaries including:

- Executive overview
- Detailed content breakdown
- Action items
- Meeting metadata

The project uses a configuration-based approach (config.yaml) for easy customization of output formats, model parameters, and summary structures, making it adaptable for various meeting types and organizational needs

---

## Setup

### Select Python Interpreter Version Between 3.8-3.11

- I am using Python 3.10.11

### Install `ffmpeg` Globally as PowerShell Administrator

**NOTE:** `ffmpeg` **DOES NOT** work in virutal environment and is required for Whisper to work. A "**[Win2]File not found error**" populates when attempting to use within a virtual environment, although  it is not best practice, utilize your global environment instead!

- Follow the instructions [HERE](https://chocolatey.org/install#individual) and install choclatey install via PowerShell Administration to install `ffmpeg`.

- Install FFmpeg:

  ```PowerShell
    choco install ffmpeg
  ```

### Requirements Installation

```bash
python3.X -m pip install -r requirements.txt --no-warn-script-location
```

### Enable Long Paths

- From PowerShell Administrator run the following:
```bash
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Download PyTorch with CUDA Support for GPU Acceleration

- If you have NVIDIA GPUs, determine what compute platform you have present:

```bash
  nvidia-smi.exe
```

- Identify "CUDA Version"
- Navigate to: <https://pytorch.org/get-started/locally/>
- Select options specific to your environment and install the command specified!
- Once installation is complete run:

```bash
  python3.X pytorch_verify.py
```

Example Successfull Output:

- **True**
- **NVIDIA GeForce RTX 3080 Ti Laptop GPU**

---

## Usage

### 0. Convert Audio to Acceptable Format

- If your audio format is not **.MP3 or .WAV**, utilize my Audio-Converter tool [HERE](https://github.com/chumphrey-cmd/Audio-Converter).


### 1. `transcribe.py` (user input) or `transcribe-args.py` (commandline arguments)

#### Simple User Input

```bash
python3.X transcribe.py
```

#### Commandline Input

##### Single File

```bash
python3.X transcribe-args.py --mode single --input-file ./path/to/audio.mp3 --output-dir ./path/to/output --model large
```

##### Multiple Files

```bash
python3.X transcribe-args.py --mode multiple --input-dir ./path/to/audio/files --output-dir ./path/to/output --model base
```

- `-h` or `--help`: To see all available options and examples

- `--mode`: Choose between 'single' or 'multiple' **REQUIRED**
  - `single`: Transcribe one audio file
  - `multiple`: Transcribe all audio files in a directory

- `--input-file`: Path to the audio file **REQUIRED**

- `--input-dir`: Path to directory containing audio files **REQUIRED**

- `--output-dir`: Directory where transcription files will be saved **REQUIRED**

- `--model`: Choose Whisper model size (If not specified, the script uses the 'base' model by default.) **OPTIONAL**
  - `tiny`: Fastest, lowest accuracy
  - `base`: Good balance of speed and accuracy
  - `small`: Better accuracy, slower than base
  - `medium`: High accuracy, slower
  - `large`: Highest accuracy, slowest

---

## 2. `summarize.py`

### Configurations

1. Download Ollama and run your chosen model, follow the process [HERE](https://ollama.com/download).
2. Configure and update the **REQUIRED** settings in the `config.yaml`

```bash
python3.X summarize.py
```

#### Example `config.yaml`

```yaml
llm: 
  model_name: "YOUR_MODEL_NAME" # REQUIRED
  max_retries: 3 # OPTIONAL
  retry_delay: 2 # OPTIONAL
  api_url: "http://localhost:11434/api/generate"
  options:
    temperature: 0.7 # OPTIONAL
    top_p: 0.9 # OPTIONAL
    max_tokens: 8000 # OPTIONAL

output:
  format: "md" # OPTIONAL
  log_file: "./data/transcript_processor.log" # REQUIRED

paths: 
  input_transcript: "./data/transcriptions/" # REQUIRED
  output_directory: "./data/meeting summaries" # REQUIRED
  audio_file: "./data/converted-audio/" # REQUIRED
  
Shortened for Space...
```

##### LLM Config Settings

- `model_name`: Choose your Ollama model
- `max_retries`: Number of API call attempts
- `retry_delay`: Delay between retries
- `temperature`: Controls response creativity, higher = more creative, lower = more concise (0.0-1.0)
- `top_p`: controls similarity sampling (accuracy) when generating a response (0.1-1)
- `max_tokens`: Maximum response length

##### Path Configuration

- `input_transcript`: Path to your transcript file
- `output_directory`: Directory for generated summaries

##### Output Settings

- `format`: Output format ('md' or 'txt')
- `log_file`: Location of log file

---

## Troubleshooting

### Ollama Connection

- Navigate to `http://localhost:11434` to ensure Ollama is running.
- From terminal input the following to identify and ensure your model is downloaded successfully:
  
   ```bash
   ollama list
   ```

   ```bash
   ollama run YOUR_MODEL
   ```

---

## TO-DO

### Command Line Overrides

Incorporation of commandline overrides should they become a repetitive occurence.

```bash
# Future implementation in summarize.py
import argparse

def parse_args():
    """Parse command line arguments for path overrides."""
    parser = argparse.ArgumentParser(description='Transcript Summarization Tool')
    parser.add_argument(
        '--input-file',
        help='Override input transcript file path from config.yaml'
    )
    parser.add_argument(
        '--output-dir',
        help='Override output directory path from config.yaml'
    )
    return parser.parse_args()
```

### Override Input File and Output Directory

```bash
python3.X summarize.py --input-file ./new/transcript.txt --output-dir ./new/output
```

### Config.yaml Command Line Arguments
- `config.yaml` should take command-line arguments rather than directy file manipulation
- User should be able to specify the title of the summary based off of the original audio file name when placed inside of "meeting summaries" so that there is clarity.

### Stream-line the Entire Process
- GOAL: Start with audio conversion (if needed) > transciption > summarization all with one command...
