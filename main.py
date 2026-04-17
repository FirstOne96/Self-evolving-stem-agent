from config import OPENAI_API_KEY

def main():
    print("Stem agent starting...")
    if not OPENAI_API_KEY:
        print("CRITICAL: API key is missing from .env")
    else:
        print(f"API key loaded: {OPENAI_API_KEY[:8]}********")


if __name__ == "__main__":
    main()
