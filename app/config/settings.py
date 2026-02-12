from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # canonical list of allowed model ids
    ALLOWED_MODEL_NAMES = [
        "llama3-70b-8192",
        "llama-3.3-70b-versatile",
        "gpt-5-nano",
    ]

    # explicit model -> provider mapping (preferred over heuristics)
    # provider values: "openai" | "groq"
    MODEL_PROVIDER = {
        "gpt-5-nano": "openai",
        "llama3-70b-8192": "groq",
        "llama-3.3-70b-versatile": "groq",
    }

    def provider_for(self, model_name: str) -> str:
        # return explicit mapping; raise for unknown models to fail-fast
        prov = self.MODEL_PROVIDER.get(model_name)
        if prov:
            return prov
        raise ValueError(f"Unknown model: {model_name}")

settings = Settings()