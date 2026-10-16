# GitHub RAG: Question Answering Over a Real Codebase

A step-by-step build of a retrieval-augmented generation (RAG) system that
answers developer questions about a GitHub repository, with answers that
point back to the source files they came from.

This is the companion code for a 14-chapter series by SNPaul Infotech.
Each chapter adds one part of the system, from architecture to deployment.

Series: [Link](https://www.snpaulinfotech.com/post/building-a-production-ready-github-rag-system)

## What it does

- Indexes a repository using code-aware chunking
- Retrieves with a mix of vector, keyword and symbol search
- Reranks results before they reach the LLM
- Checks who may see which code before retrieval
- Returns answers with references to the files they came from

## Why not just paste the repo into an LLM?

Whole-repo prompts get slower, costlier and less accurate as the repo grows,
and they cannot control who sees which code. Chapter 1 works through the
cost comparison with stated assumptions.

## How this repo maps to the series

The `main` branch holds the latest code. Each chapter learnings can be taken and built using the series in the blog.


## Prerequisites

The following commands are intended for **Windows Command Prompt (CMD)**.

### 1. Verify `uv` Installation

Check whether `uv` is installed and available:

```cmd
uv --version
```

Example output:

```text
uv 0.x.x
```

The exact version may vary.

### 2. Check Available Python Installations

List the Python versions available through `uv`:

```cmd
uv python list
```

### 3. Install Python 3.11

If Python 3.11 is not already available, install it using:

```cmd
uv python install 3.11
```

### 4. Verify Python Installation

Confirm that Python 3.11 is available and working:

```cmd
uv run --python 3.11 python --version
```

Expected output:

```text
Python 3.11.x
```

The exact patch version may vary.

## Notes

This project was written independently and contains no employer or client
code or data.

## Contact

SNPaul Infotech: [SNPaulInfotech](www.snpaulinfotech.com)
