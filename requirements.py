import subprocess
import sys

def install_dependencies():
    dependencies = [
        "streamlit",
        "langchain",
        "langchain-core",
        "langchain-google-genai",
        "langgraph",
        "mcp",
        "sqlmodel",
        "python-dotenv",
        "pydantic",
        "zscaler-sdk-python",
        "langchain-mcp-adapters",
        "pycountry",
        "uvicorn",
        "Pillow"
    ]
    
    print("Installing dependencies...")
    for package in dependencies:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            
    print("\nAll dependencies processed.")

if __name__ == "__main__":
    install_dependencies()
