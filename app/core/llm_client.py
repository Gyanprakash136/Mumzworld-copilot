import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL = "llama-3.3-70b-versatile"   # Groq-hosted Llama 3.3 70B, free tier


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set in .env\n"
                "Get a free key at: https://console.groq.com"
            )
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

    def generate(self, prompt: str, **kwargs) -> str | None:
        """Call Llama 3.3 70B via Groq. Returns None on failure."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  Llama call failed: {e}")
            return None

    def generate_json(self, prompt: str, **kwargs) -> dict | None:
        """
        Generate and parse a JSON response from Llama.
        Strips markdown code fences automatically.
        Returns None on any failure — callers must handle this explicitly.
        """
        content = self.generate(prompt)
        if not content:
            return None

        # Strip ```json ... ``` or ``` ... ``` wrappers the model sometimes adds
        if "```json" in content:
            content = content.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in content:
            content = content.split("```", 1)[1].split("```", 1)[0].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}\nRaw snippet: {content[:300]}")
            return None
