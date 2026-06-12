export const MOCK_PROMPT = "I have to decide which models to run on my laptop. Help me with it. I have uploaded `input.txt` and two screenshots of my system specs (`ss1.png` and `ss2.png`).";

export const getMockResponse = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        answer: `Based on the Ollama models listed in your sources and the hardware specifications detected in your screenshots (**ss1.png** and **ss2.png**), here is a tailored recommendation for your laptop.

### Hardware Analysis (From Screenshots)
Your system screenshots show an **Intel/AMD CPU with 16GB of System RAM** and no dedicated VRAM. 
- Because you have 16GB of RAM, you can comfortably run models up to **14B parameters** using CPU memory.
- Models requiring 20GB+ VRAM (like Qwen 3 Coder 32B or Llama 4 70B+) will exhaust your memory and cause severe system swapping or crashes.

### Recommended Models for Your Laptop
1. **Gemma 4 (E2B / E4B)**: Since these are specifically optimized for mobile and edge deployment, they will run blazingly fast on your laptop's CPU. Perfect for quick logic and background agent tasks.
2. **Qwen 2.5 (7B)**: A fantastic middle ground. It's listed in the text as "CPU Friendly" and excels at coding tasks while easily fitting into your 16GB RAM (only requires ~4.7 GB).
3. **Phi-4 (~14B)**: For complex reasoning, this "Small Model, Big Brain" is designed to be efficient on consumer hardware. It will use about 8-10GB of your RAM, leaving enough for your OS to run smoothly.

*Avoid*: **Mistral Large 2** (>60GB), **Qwen 3 Coder** (32B), and **Llama 4** (70B+), as the text explicitly states these are NOT CPU-friendly and require heavy multi-GPU setups.`,
        context: {
          vector_chunks: [
            "[FILE: input.txt] Most models under 7B parameters run efficiently on modern CPUs. Larger models (11B+) generally require a dedicated GPU or significant system RAM (slow on CPU).",
            "[FILE: input.txt] Phi-4 (Microsoft): ~14B. Size: ~8-10 GB. High-quality reasoning and logic tasks where efficiency is key. Works on CPU? Yes. Designed to be efficient on consumer hardware.",
            "[IMAGE-ANALYSIS: ss1.png | Source: Vision-LLM] The screenshot displays a 'System Information' window showing a modern CPU with 16.0 GB of installed RAM and integrated graphics."
          ],
          vector_images: [
            "/ss1.png",
            "/ss2.png"
          ],
          graph_relationships: [
            "(input.txt)-[:LISTS]->(Phi-4)",
            "(Phi-4)-[:REQUIRES]->(10GB_RAM)",
            "(User_System_ss1.png)-[:HAS_CAPACITY]->(16GB_RAM)",
            "(16GB_RAM)-[:SATISFIES]->(Phi-4_Requirements)"
          ],
          causal_chains: [
            "ss1.png(16GB_RAM) -> Fits_Under_12GB_Models -> Qwen2.5_7B_Runs_Smoothly",
            "input.txt(32B_Model) -> Requires_20GB_VRAM -> Exceeds_16GB_System_RAM -> Hardware_Failure"
          ]
        }
      });
    }, 1800);
  });
};
