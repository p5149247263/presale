import React, { useEffect, useState } from "react";
import { getLlmConfig, setLlmConfig } from "../api/client";

export function ModelConfigPage() {
  const [provider, setProvider] = useState<"openai" | "anthropic" | "local" | "mock">("mock");
  const [model, setModel] = useState("gpt-4o-mini");
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(1200);
  const [saved, setSaved] = useState<any>(null);

  useEffect(() => {
    getLlmConfig().then((cfg) => {
      setProvider(cfg.provider);
      setModel(cfg.model);
      setTemperature(cfg.temperature);
      setMaxTokens(cfg.max_tokens);
    });
  }, []);

  return (
    <section className="card">
      <h2>Model Provider Config</h2>
      <label>Provider</label>
      <select value={provider} onChange={(e) => setProvider(e.target.value as any)}>
        <option value="mock">mock</option>
        <option value="openai">openai</option>
        <option value="anthropic">anthropic</option>
        <option value="local">local</option>
      </select>
      <input value={model} onChange={(e) => setModel(e.target.value)} placeholder="Model name" />
      <label>Temperature</label>
      <input type="number" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} step="0.1" min="0" max="1" />
      <label>Max tokens</label>
      <input type="number" value={maxTokens} onChange={(e) => setMaxTokens(Number(e.target.value))} step="100" min="200" />

      <button
        onClick={async () => {
          const out = await setLlmConfig({ provider, model, temperature, max_tokens: maxTokens });
          setSaved(out);
        }}
      >
        Save Model Config
      </button>

      {saved && <pre>{JSON.stringify(saved, null, 2)}</pre>}
    </section>
  );
}
