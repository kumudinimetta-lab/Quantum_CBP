<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.
# AGENTS.md — Research Rules

## Core Rule
Determine what is true. Do not optimize to strengthen, defend, prove, or validate the paper.

Evidence → assumptions → derivation/experiment → adversarial check → claim.

Never reason backward from a desired claim.

## Mathematical Claims
For every theorem or complexity claim:
- Read the primary source, not summaries.
- Record the exact theorem/lemma number and assumptions.
- Map every symbol to the implementation.
- State what the theorem does AND does not imply.
- Attempt a counterexample.
- If uncertain, stop and report `UNRESOLVED`.

Never replace a concept with a related one: effective spectral gap ≠ minimum spectral gap; query complexity ≠ runtime; upper bound ≠ measured value.

## Code and Experiments
Executable code and raw data are the source of truth.
Trace the actual call path and metric definition before describing results.

Classify every metric as:
`MEASURED`, `DERIVED`, `SCHEDULED`, `SIMULATED`, or `HARDCODED`.

Never call a derived or scheduled metric an empirical measurement.

Before any regression, verify the dependent variable is not computed from the predictor. If it is, report `CIRCULAR_VALIDATION` and stop.

Never manually edit raw experimental data. If modified, mark it `CONTAMINATED` and regenerate from code.

Never silently drop failed, capped, or trivial instances.

## Claims
For every major claim, first try to falsify it.

Explicitly audit words:
`first`, `novel`, `exact`, `optimal`, `always`, `never`, `speedup`, `advantage`, `proves`, `confirms`, `validates`.

Use the weakest wording supported by evidence.

## Workflow
1. Audit.
2. Verify primary sources, code, and raw data.
3. Run experiments if needed.
4. Decide the strongest defensible claim.
5. Edit the paper.
6. Adversarially re-audit.

Do not derive a central claim and approve it in the same pass.

## Stop Conditions
Immediately stop and report `RESEARCH_INTEGRITY_STOP` if:
- a theorem interpretation is uncertain;
- code differs from the paper;
- metric semantics are unclear;
- validation is circular;
- raw data was manually modified;
- sample counts conflict;
- a citation points to the wrong paper.

Correctness and reproducibility always take priority over stronger paper claims.
### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
