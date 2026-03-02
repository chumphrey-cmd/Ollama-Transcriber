import torch

print("\n--- Hardware Acceleration Check ---")

if torch.cuda.is_available():
    device_name = torch.cuda.get_device_name(0)
    print(f"✅ SUCCESS: CUDA is available!")
    print(f"🎮 GPU Detected: {device_name}")
    print("⚡ Transcription will be hardware-accelerated and fast.")
else:
    print("⚠️  WARNING: CUDA (GPU) is NOT available.")
    print("💻 PyTorch will fall back to using your CPU.")
    print("🐌 NOTE: Transcription will be highly resource-intensive and significantly slower.")

print("-----------------------------------\n")