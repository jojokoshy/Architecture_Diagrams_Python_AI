<!-- Auto-generated guidance for AI coding agents working on this repo. -->
# Copilot instructions — Architecture_Diagrams_Python_AI

Purpose: provide concise, actionable guidance so an AI coding agent (or a new contributor) can be immediately productive in this workspace.

Quick summary
- Project purpose: generate Azure architecture diagrams from Python scripts and by parsing IaC (Terraform, Bicep, ARM). The primary working folder is `Arch_Diagrams/`.
- Primary outputs: `diagrams/*.png`, `diagrams/*.dot`, `diagrams/*.drawio` (DOT is the canonical text artifact).

Essential setup (Windows / PowerShell)
- Install GraphViz (native binary) first and add it to PATH. Typical path: `C:\Program Files\Graphviz\bin`.
- Create & activate Python venv inside `Arch_Diagrams/`:
```
cd Arch_Diagrams
python -m venv venv
.\venv\Scripts\Activate.ps1
```
- Install requirements. Note: `pygraphviz` requires GraphViz dev files and an MSVC build toolchain. Install `pygraphviz` before the rest (example shown):
```
# Example: set GRAPHVIZ_DIR and install pygraphviz
$env:GRAPHVIZ_DIR = 'C:\Program Files\Graphviz'
pip install --config-settings="--global-option=build_ext" --config-settings="--global-option=-IC:\Program Files\Graphviz\include" --config-settings="--global-option=-LC:\Program Files\Graphviz\lib" pygraphviz
pip install -r requirements.txt
```

Where to run work and common commands
- Working dir: `Arch_Diagrams/` (contains scripts, `requirements.txt`, and `diagrams/` output folder).
- Run a manual diagram generator: `python contoso_architecture.py` (creates `diagrams/contoso_architecture.*`).
- Run Terraform parser: `python terraform_to_diagram.py "path/to/main.tf" "project_name"`.
- GraphViz → Draw.io conversion is automated in scripts via `graphviz2drawio`; ensure `graphviz2drawio` is on PATH after pip install.

Key files and patterns (direct references)
- `Arch_Diagrams/agent.md` — high-value agent instructions and environment notes. Use this as the canonical list of environment steps and examples.
- `Arch_Diagrams/requirements.txt` — exact Python deps and notes about `pygraphviz` and GraphViz.
- `Arch_Diagrams/terraform_to_diagram.py` — parser for Terraform files; it extracts `resource "type" "name"` blocks, `depends_on`, and reference patterns like `azurerm_*` to infer relationships.
- `Arch_Diagrams/contoso_architecture.py` — manual example showing cluster usage, tier color patterns, and graph attributes.
- `Arch_Diagrams/bicep_*` and `arm_*` scripts — show parsing approaches and common limitations (Bicep modules often require manual inspection).

Project-specific conventions & patterns
- Clusters: use `Cluster(...)` to group VNets, subnets, and tiers. The codebase relies on cluster background colors to visually separate tiers (see `agent.md` color examples).
- Icon naming: class names are case-sensitive and may differ from common guesses. Example: use `PublicIpAddresses` (correct) not `PublicIPAddresses` (wrong). When unsure, import the module and `print(dir(module))` to list symbols.
- Graph attributes: scripts use `graph_attr` with `splines='ortho'`, `nodesep`, `ranksep` and `fontsize` to produce orthogonal, readable layouts — keep these when making new scripts.
- Outputs: DOT files are the primary machine-readable artifact — commit DOTs for PRs so reviewers can see textual diffs.

Parsing notes & limitations (important for automation)
- Terraform parsing is regex-based and infers `depends_on` and resource references. It works best on flattened, single-file examples (see `terraform-demo/main.tf`).
- Bicep parsing is fragile due to modules and parameter passing; prefer scenario-specific generators for complex Bicep projects.
- ARM templates: scripts parse the `resources` array and map `Microsoft.*` types to diagram icon classes. Confirm mappings when new resource types appear.

Troubleshooting (common, actionable fixes)
- Error: `ExecutableNotFound: failed to execute WindowsPath('dot')` → add GraphViz bin dir to PATH and restart the shell:
```
$env:PATH += ';C:\Program Files\Graphviz\bin'
```
- Error: `cannot import name 'PublicIPAddresses'` → check class name in module; correct example: `PublicIpAddresses`.
- Error: `pygraphviz` build fails → ensure Visual Studio Build Tools / MSVC is installed and GraphViz include/lib paths are set during pip install (see install snippet above).

Developer workflows & PR guidance
- Run generation locally and include DOT + PNG outputs in PR where the diagram is being added/changed.
- Keep DOT files minimal and meaningful; reviewers will look at DOT diffs to understand automated changes.
- If auto-generation produces a cluttered layout, commit the DOT and an updated `.drawio` (editable) after manual refinement.

Examples to paste when reproducing work
- Create venv & run a sample script:
```
cd Arch_Diagrams
python -m venv venv
.\venv\Scripts\Activate.ps1
$env:PATH += ';C:\Program Files\Graphviz\bin'
python contoso_architecture.py
```
- Run Terraform parser on the demo:
```
python terraform_to_diagram.py ..\terraform-demo\main.tf sc_demo
```

What I (the AI) should not assume
- Do not assume pygraphviz is installed system-wide; the repository expects GraphViz native binaries and a correctly built pygraphviz.
- Do not assume Bicep/module references are automatically resolvable; treat Bicep parsing as best-effort and flag complex cases for human review.

If something is unclear or you want me to expand a section (examples, tests, or PR checklist), tell me which area to iterate on.
