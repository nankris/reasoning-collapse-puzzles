Working editorial outline, prepared during inference. Replace with measured results in blog.md.

Hook: Apple says frontier reasoning models face a “complete accuracy collapse beyond certain complexities.” Source: https://arxiv.org/abs/2506.06941 . For an engineer this sounds like a warning about long exact workflows. Ask what the benchmark is actually asking the model to produce.

Competing explanation: Lawsen's v2 https://arxiv.org/abs/2506.09250 distinguishes knowing an algorithm from writing thousands of steps. It corrects the earlier token arithmetic, so do not repeat the first version's stronger claim that the outputs must exceed the budget. Program success changes the system, and cannot prove flawless unaided execution.

What I tested: 4B pilot, 8B official AWQ confirmation; 750 responses, 25 per level/mode/representation; Hanoi 3..10, checkers 2..5; program 8..10. NVIDIA L4, vLLM offline engine, same max_tokens=16384, temp=.6/top_p=.95/top_k=20; deterministic state verifier. Paired random peg names/instance nonces and independent fixed generation seeds. Fresh isomorphic variants, not 750 unique algorithms. Same ceiling, not same actual compute.

Preregistered tests: H1 >10pp ON advantage at 4..6; H2 <10% at >=7 in each mode with per-cell cap gate; H3 >=20% rise 3->5 and >=20% fall 5->10, cap gate; H4 >50pp program improvement at 8..10 pooled modes. Frozen commit ba49376, before any confirmation. Small pilot truncated at 18/36; pending responses not failures. Forecast threshold is a fragile error-accumulation extrapolation, not a law.

Result figures: accuracy.png, thinking_tokens.png, truncation.png, table.png. Setup illustration diagram.png (editable diagram.excalidraw). One headline number with paired CI, then exact counts. Describe endpoint Wilson vs bootstrap intervals. If cap >5%, H2/H3 censored under frozen rules, regardless of dramatic curve.

What surprised me / what I got wrong: report all failed predictions and fixed peak. Do not replace n=5 by the prettiest post-hoc maximum. Declining exact accuracy alone does not establish the entire three-regime account.

Production recommendations: use executable specifications where the structure permits; separate proposal from deterministic execution; validate every state transition and final goal; classify length/format/illegal-state failures; budget and log actual token consumption. Retain a strict enumerated-output test where literal enumeration is the product requirement.

Limitations: one small quantized open model, two toy families, no frontier-model replication; alpha labels and nonces do not create different mathematical structures; no training-contamination claim; code arm receives interpreter; 25 per cell is coarse; single stochastic generation per instance, no seed replication; truncation is an experimental constraint; no causal generalization to abstract reasoning capacity.

Close on engineering criterion: measure whether the system delivers a valid artifact at a known cost. Code: <repo link placeholder>.
