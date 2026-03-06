import os
from huggingface_hub import hf_hub_download

MODEL_REPO = "DomSimone/Umbuzo"
# Switched to a 4-bit quantized model to reduce memory usage.
# PLEASE VERIFY THIS FILENAME EXISTS IN THE HUGGING FACE REPOSITORY.
MODEL_FILENAME = "umbuzo-gemma-2b-v3data.q4_K_M.gguf"

def download_model():
    print(f"Downloading {MODEL_FILENAME} from {MODEL_REPO}...")
    try:
        # This will download the model to the default Hugging Face cache directory
        path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILENAME)
        print(f"Model downloaded to: {path}")
    except Exception as e:
        print(f"Failed to download model: {e}")
        # We don't exit with error here to allow the build to proceed if token is missing,
        # but it means runtime download will be needed.
        pass

if __name__ == "__main__":
    download_model()
