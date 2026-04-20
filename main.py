from html import parser
import logging
import sys
from pathlib import Path
import whisper
import argparse

# Add project root to Python path for proper import resolution
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Ensure the user is running a supported Python version (3.8+)
if sys.version_info < (3, 8):
    print("ERROR: Unsupported Python Version")
    print(f"You are running Python {sys.version_info.major}.{sys.version_info.minor}.")
    print("Ollama Transcriber requires Python 3.8 or later.")
    print("Please use the correct version or activate your virtual environment.\n")
    sys.exit(1)

# Import custom modules for audio processing, transcription, and summarization
from src.utils.config import ConfigManager
from src.audio.converter import convert_audio
from src.transcription.transcribe import transcribe_audio
from src.summary.summarize import TranscriptSummarizer
from src.utils.input_handler import select_audio_file


def parse_arguments():
    """
    Parse command line arguments for the audio transcription and summarization tool.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Audio Transcription and Summarization Tool",
        epilog="""
Examples:
    # Use GUI to select audio file
    python main.py --gui
    
    # Process specific audio file with default settings
    python main.py --audio path/to/recording.mp3
    
    # Specify output directory and Whisper model
    python main.py --audio path/to/recording.mp3 --output path/to/output --transcript medium
    
    # Use specific LLM model
    python main.py --audio path/to/recording.mp3 --llm mistral:latest
    
    # Full example with all options
    python main.py --audio path/to/recording.mp3 --output path/to/summaries --transcript medium --llm mistral:latest
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,  # Preserves formatting in epilog
    )

    parser.add_argument(
        "--audio", type=str, help="Path to audio file to transcribe and summarize"
    )

    parser.add_argument(
        "--output", type=str, help="Path to output directory for saving summaries"
    )

    parser.add_argument(
        "--llm",
        type=str,
        help="Name of Ollama model to use for summarization (default: from config.yaml)",
    )

    parser.add_argument(
        "--transcript",
        type=str,
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model selection for transcription (default: from config.yaml)",
    )

    parser.add_argument(
        "--language",
        type=str,
        help='Language code for transcription (e.g., "en" for English, "es" for Spanish, "fr" for French). Use "auto" for detection. See README for the full list of supported languages.',
    )

    parser.add_argument(
        "--gui", action="store_true", help="Launch GUI file picker to select audio file"
    )

    return parser.parse_args()


def main():
    """
    Main entry point for the audio processing, transcription, and summarization pipeline.

    Workflow:
    1. Parse command line arguments
    2. Configuration loading and logging setup
    3. Audio format conversion (if needed)
    4. Whisper model initialization
    5. Audio transcription
    6. Transcript summarization

    All paths and settings are driven by config.yaml configuration with optional
    overrides from command line arguments.
    """
    logging.getLogger().setLevel(logging.INFO)  # Add this line
    logging.info("Testing basic logging in main()")  # Add this line
    try:
        # Step 1: Parse command line arguments
        args = parse_arguments()

        # Step 2: Configuration Loading and Logging Setup
        config_manager = ConfigManager()
        config = config_manager.config

        # Process command line arguments to override config settings
        # If GUI flag is set, launch file picker
        if args.gui:
            file_path = select_audio_file()
            if file_path:
                config["paths"]["audio_file"] = file_path
                print(f"Selected audio file: {file_path}")
            else:
                print("No audio file selected. Exiting.")
                sys.exit(1)
        # Otherwise use CLI arguments if provided
        elif args.audio:
            config["paths"]["audio_file"] = args.audio
            print(f"Using audio file from command line: {args.audio}")

        # Update other config values if provided
        if args.output:
            config["transcription"]["meeting_summary_directory"] = args.output
            print(f"Output directory set to: {args.output}")
        if args.llm:
            config["llm"]["model_name"] = args.llm
            print(f"LLM model set to: {args.llm}")
        if args.transcript:
            config["transcription"]["model_selection"] = args.transcript
            print(f"Whisper model set to: {args.transcript}")

        logging.info("Configuration loaded and logging initialized.")

        # Log the configuration settings being used
        logging.info(f"Audio file: {config['paths']['audio_file']}")
        logging.info(
            f"Output directory: {config['transcription']['meeting_summary_directory']}"
        )
        logging.info(f"LLM model: {config['llm']['model_name']}")
        logging.info(f"Whisper model: {config['transcription']['model_selection']}")

        # Step 3: Audio Processing and Conversion
        # Construct paths using PathLib for cross-platform compatibility
        audio_file_path = Path(config["paths"]["audio_file"])

        # Verify that audio file exists
        if not audio_file_path.exists():
            logging.error(f"Audio file not found: {audio_file_path}")
            print(f"Error: Audio file not found: {audio_file_path}")
            sys.exit(1)

        converted_audio_dir = Path(
            config["audio_processing"]["converted_audio_directory"]
        )
        output_format = config["audio"]["output_format"]

        # Create converted audio directory if it doesn't exist
        converted_audio_dir.mkdir(parents=True, exist_ok=True)

        # Check if audio format conversion is needed
        try:
            print("Trying to convert audio")  # Add this line
            logging.info("Trying to convert audio")  # Add this line
            if audio_file_path.suffix.lower() != f".{output_format}":
                # Generate path for converted audio file
                converted_audio_path = (
                    converted_audio_dir / f"{audio_file_path.stem}.{output_format}"
                )
                logging.info(f"Converting {audio_file_path} to {output_format}")
                print(f"Converting audio to {output_format} format...")

                # Attempt audio conversion
                if not convert_audio(
                    str(audio_file_path), output_format, str(converted_audio_path)
                ):
                    raise ValueError(f"Audio conversion failed for {audio_file_path}")
                logging.info(f"Audio converted successfully to: {converted_audio_path}")
                print(f"Audio converted successfully")

                # Update path to use converted audio
                audio_file_path = converted_audio_path
            else:
                logging.info("Audio already in correct format. Skipping conversion.")
                print("Audio already in correct format. Skipping conversion.")
        except RuntimeError as e:
            print(f"Exception caught in audio conversion: {e}")
            logging.error(f"FFmpeg Error during conversion: {e}")
            print(
                "FFmpeg not found. Please ensure ffmpeg is installed and in your PATH.\n"
                "  Linux:   sudo apt install ffmpeg   (or your distro's package manager)\n"
                "  macOS:   brew install ffmpeg\n"
                "  Windows: choco install ffmpeg"
            )
            sys.exit(1)
        except ValueError as e:
            print(f"Exception caught in audio conversion: {e}")
            logging.error(f"Error during audio conversion: {e}")
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Exception caught in audio conversion: {e}")
            logging.error(f"Unexpected error during audio conversion: {e}")
            print(f"Error: {e}")
            sys.exit(1)

        # Step 4: Load Whisper Model
        try:
            logging.info(
                f"Loading Whisper model: {config['transcription']['model_selection']}"
            )
            print(
                f"Loading Whisper model '{config['transcription']['model_selection']}' on device..."
            )
            model = whisper.load_model(config["transcription"]["model_selection"])
            logging.info("Whisper model loaded successfully")
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Exception caught loading whisper model: {e}")
            logging.error(f"Error loading Whisper model: {e}")
            print(f"Error: {e}")
            sys.exit(1)

        # Step 5: Audio Transcription
        try:
            logging.info("Starting audio transcription...")
            print("Starting audio transcription...")

            # Determine the target language.
            # It checks CLI arguments first, then falls back to config.yaml.
            # We use .get('language', 'en') to safely default to English if the key is missing.
            target_language = (
                args.language
                if args.language
                else config["transcription"].get("language", "en")
            )

            # Whisper expects `None` if we want it to auto-detect the language.
            if target_language.lower() == "auto":
                target_language = None

            # Let the user know what language is being used
            print(f"Using language: {target_language or 'auto-detect'}")

            # Ensure transcription directory exists
            transcription_dir = Path(config["transcription"]["transcription_directory"])
            transcription_dir.mkdir(parents=True, exist_ok=True)

            # Perform audio transcription, now passing the target_language
            transcribe_audio(
                str(audio_file_path),
                str(transcription_dir),
                model,
                language=target_language,
            )

            # Construct path to the transcript file
            transcript_path = transcription_dir / f"{audio_file_path.stem}.txt"
            logging.info(f"Transcription saved to: {transcript_path}")
            logging.getLogger().handlers[0].flush()
            print(f"Transcription saved to: {transcript_path}")

        except Exception as e:
            print(f"Exception caught in audio transcription: {e}")
            logging.error(f"Audio transcription failed: {e}")
            print(f"Error: {e}")
            sys.exit(1)

        # Step 6: Transcript Summarization
        try:
            logging.info("Starting summary generation...")
            print("Starting summary generation...")

            # Initialize and use TranscriptSummarizer
            summarizer = TranscriptSummarizer(config)
            summary_path = summarizer.process_transcript(
                transcript_path=str(transcript_path), audio_path=str(audio_file_path)
            )
            logging.info(f"Summary generated and saved to: {summary_path}")
            print(f"Summary generated and saved to: {summary_path}")
            logging.info("Complete pipeline executed successfully")
            print("Complete pipeline executed successfully")
        except Exception as e:
            print(f"Exception caught in summary generation: {e}")
            logging.error(f"Summary generation failed: {e}")
            print(f"Error: Summary generation failed: {e}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Main process failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

