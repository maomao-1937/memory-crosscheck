# MemoryCrosscheck

MemoryCrosscheck compares factual lines in an older agent-memory Markdown file with a current Markdown document. A local natural-language-inference model flags **possible** contradictions and reports both line numbers for human review. The files are never edited or uploaded. This is a small audit tool, not a memory database or automatic instruction-precedence engine.

## For whom and what task

For people maintaining coding-agent memory or project notes. Before reusing old notes, run a read-only comparison against current project facts; inspect flagged pairs and decide whether the old memory needs updating. Non-goals: silently rewriting memory, evaluating policy authority, exhaustive fact checking against code or the web, or resolving conflicts without a human.

## Install and run

Python 3.11+ is required. First run downloads the [Apache-2.0 English NLI model](https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768); inference is local afterward and needs no API key.

```bash
uv sync --python 3.11
uv run memory-crosscheck --current examples/current.md --memory examples/memory.md --out report.local.json
cat report.local.json
uv run python -m unittest discover -s tests -v
```

The example contrasts an old US-East deployment fact with a current EU-West fact. The report gives each possible conflict's source lines and a model contradiction signal. **That signal is not a calibrated probability that either file is true.** Check dates and authoritative sources before changing any memory.

Only prose lines from the two Markdown files are considered; headings, tables, block quotes and fenced code are skipped. The MVP accepts at most 40 factual lines per file. Split large files by topic. All eligible line pairs are compared, so cost grows quadratically; this is intentionally a scoped review, not whole-workspace indexing.

## Product rationale

On 2026-10-09, we examined independent reports: an [OpenClaw discussion from May 2026](https://github.com/openclaw/openclaw/issues/82925) warns that volatile operational facts in agent memory become stale; an [August Codex report](https://github.com/openai/codex/issues/39223) documents old memory conflicting with current instructions; and a [September Deep Agents report](https://github.com/langchain-ai/deepagents/issues/6044) shows stale loaded memory after its source changed. These establish recurring friction in agent-memory workflows, not measured demand for this particular CLI.

The [claude-mem](https://github.com/thedotmack/claude-mem) and [memo](https://github.com/jagoff/memo) projects show sustained open-source activity around persistent agent memory. `memo` already includes a contradiction radar; MemoryCrosscheck is not presented as novel contradiction science. Its narrow difference is a zero-setup, provider-independent, read-only comparison of two existing Markdown files with line-level audit output, for people who do not want to migrate into a memory platform. Whether that is an attractive enough wedge remains a user-validation hypothesis. No code is copied from those projects.

## Known limitations and acceptance

- The model was trained on English sentence pairs. Imperatives, Chinese text, negation, dates, numbers, and domain-specific facts may yield false positives or misses.
- The tool compares text to text, not text to a live system. A newer file is not automatically correct.
- Documents longer than 40 factual lines must be scoped manually; the model truncates each pair to 512 tokens.
- A clean-environment example run, passing unit tests, unchanged input files, and reviewable line references are the MVP acceptance criteria. Real users have not yet validated usefulness.

Application code is MIT licensed. Model weights are downloaded separately under the model's Apache-2.0 license.
