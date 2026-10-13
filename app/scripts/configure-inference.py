#!/usr/bin/env python3
"""Generate a local gateway config for the selected inference provider.

Uses only the standard library. Provider credentials remain environment
references in the generated YAML, never copied into it.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "openai": {
        "support-model": "openai/gpt-5.4-2026-03-05",
        "embedding": "openai/text-embedding-3-small",
        "eval-nano": "openai/gpt-5-nano-2025-08-07",
        "eval-54": "openai/gpt-5.4-2026-03-05",
        "eval-5": "openai/gpt-5",
    },
    "openrouter": {
        "support-model": "openrouter/openai/gpt-5.4",
        "embedding": "openrouter/openai/text-embedding-3-small",
        "eval-nano": "openrouter/openai/gpt-5-nano",
        "eval-54": "openrouter/openai/gpt-5.4",
        "eval-5": "openrouter/openai/gpt-5",
    },
}


def read_env(path):
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")
    return values


def render_config(source, provider):
    if provider not in ROUTES:
        raise ValueError("INFERENCE_PROVIDER must be openai or openrouter")
    key = "OPENAI_API_KEY" if provider == "openai" else "OPENROUTER_API_KEY"
    current = None
    output = []
    for line in source.splitlines():
        if line.startswith("  - model_name:"):
            current = line.split(":", 1)[1].strip()
        if current in ROUTES[provider]:
            if line.startswith("      model:"):
                line = "      model: " + ROUTES[provider][current]
            elif line.startswith("      api_key:"):
                line = "      api_key: os.environ/" + key
        output.append(line)
    return "\n".join(output) + "\n"


def main():
    values = read_env(ROOT / ".env")
    provider = os.environ.get("INFERENCE_PROVIDER", values.get("INFERENCE_PROVIDER", "openai")).strip().lower()
    try:
        result = render_config((ROOT / "infra/litellm.yaml").read_text(), provider)
    except ValueError as error:
        raise SystemExit(str(error))
    # Keep prepared native-routing aliases when changing the inference provider.
    routing_models = ROOT / "infra/routing-demo.models.yaml"
    if routing_models.exists():
        result = result.replace("\nlitellm_settings:", "\n" + routing_models.read_text() + "\nlitellm_settings:", 1)
    # Preserve the optional Lakera guardrail when switching inference routes.
    # Keep credential values out of the generated configuration.
    if os.environ.get("LAKERA_API_KEY") or values.get("LAKERA_API_KEY"):
        fragment = (ROOT / "infra/lakera-guardrail.fragment.yaml").read_text()
        if os.environ.get("LAKERA_PROJECT_ID") or values.get("LAKERA_PROJECT_ID"):
            fragment += "      project_id: os.environ/LAKERA_PROJECT_ID\n"
        result += "\n" + fragment
    (ROOT / "infra/litellm.provider.generated.yaml").write_text(result)
    print("Inference provider: " + provider + " (chat, embeddings and OpenAI evaluation models)")


if __name__ == "__main__":
    main()
