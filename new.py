# --- HUGGING FACE MODEL CONFIGURATION ---
MODEL_REPO = "DomSimone/Umbuzo"
MODEL_FILENAME = "umbuzo-gemma-2b-v3data.f16.gguf"
# ----------------------------------------

llm = None


def load_model():
    global llm
    try:
        logger.info(f"Attempting to download model '{MODEL_FILENAME}' from Hugging Face repo '{MODEL_REPO}'...")
        # You can set a Hugging Face token as an environment variable HF_TOKEN
        # if the model is private or if you encounter rate limiting.
        # hf_token = os.getenv("HF_TOKEN")
        llm = Llama.from_pretrained(
            repo_id=MODEL_REPO,
            filename=MODEL_FILENAME,
            # token=hf_token, # Uncomment and set HF_TOKEN if needed
            n_ctx=4096,
            n_threads=4,
            verbose=True
        )
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to load model: {e}")
        print(f"Error details: {e}")
        print(f"Please verify the Hugging Face repository ID '{MODEL_REPO}' and filename '{MODEL_FILENAME}'.")
        print(
            "Ensure you have an active internet connection and that the repository is publicly accessible or you have set the HF_TOKEN environment variable if it's private.")
