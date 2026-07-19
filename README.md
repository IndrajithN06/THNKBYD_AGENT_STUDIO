# THNKBYD AI Agent Studio

> An AI-powered multi-agent pipeline that transforms a simple topic into visual storytelling assets for cinematic YouTube videos.

---

# Overview

THNKBYD AI Agent Studio is a local-first AI content generation system built using an agentic architecture.

The goal is to automate the creative workflow from a single topic into:

- Script
- Storyboard
- Image Prompts
- AI Generated Images
- (Upcoming) Voiceover
- (Upcoming) Final Video

The project is designed with modular agents so that each stage can be improved independently.

---

# Current Pipeline

```
User Topic
      │
      ▼
Director Agent
      │
      ▼
Script Writer Agent
      │
      ▼
Storyboard Agent
      │
      ▼
Image Prompt Agent
      │
      ▼
Image Generator Agent
      │
      ▼
ComfyUI
      │
      ▼
Generated Images
```

---

# Project Structure

```
app/
│
├── agents/
│   ├── director.py
│   ├── script_writer.py
│   ├── storyboard_writer.py
│   ├── image_prompt_writer.py
│   └── image_generator.py
│
├── config/
│
├── models/
│
├── prompts/
│
├── tools/
│   ├── llm_client.py
│   ├── comfy_client.py
│   ├── comfy_backend.py
│   ├── image_service.py
│   ├── file_writer.py
│   └── resource_loader.py
│
├── workflows/
│   └── dreamshaper_workflow.json
│
└── main.py
```

---

# Agent Responsibilities

## Director Agent

Coordinates the complete pipeline.

Responsibilities

- Receives the user topic
- Executes every agent
- Saves outputs
- Handles workflow orchestration

---

## Script Writer Agent

Generates the long-form educational script.

Output

```
outputs/scripts/
```

---

## Storyboard Agent

Breaks the script into cinematic scenes.

Output

```
outputs/storyboards/
```

---

## Image Prompt Agent

Converts storyboard scenes into high-quality AI image prompts.

Each scene contains:

- Image Prompt
- Animation Notes
- Assets Needed

Output

```
outputs/image_prompts/
```

---

## Image Generator Agent

Generates one image per storyboard scene.

Uses:

- ImageService
- ComfyBackend
- ComfyClient

Output

```
outputs/images/
```

---

# Technologies Used

## LLM

- Ollama
- Gemma 3

Used for

- Script generation
- Storyboards
- Image prompts

---

## Image Generation

- ComfyUI
- DreamShaper 8

Workflow

```
Topic
↓

Scene Prompt

↓

ComfyUI API

↓

PNG Image
```

---

# Architecture

The project follows dependency injection.

```
Director

↓

ImageGeneratorAgent

↓

ImageService

↓

ImageBackend Interface

↓

ComfyBackend

↓

ComfyClient

↓

ComfyUI REST API
```

This allows changing the image backend without changing the agent.

Possible future backends:

- Stable Diffusion API
- OpenAI Images API
- Replicate
- Fal AI
- Local Flux

---

# Outputs

Current generated assets

```
outputs/

├── scripts/
├── storyboards/
├── image_prompts/
└── images/
```

---

# Current Features

✅ Director Agent

✅ Script Generation

✅ Storyboard Generation

✅ Image Prompt Generation

✅ ComfyUI Integration

✅ Automatic Image Generation

✅ Automatic Image Saving

✅ Modular Backend Architecture

---

# Roadmap

## Completed

- Milestone 1
    - Project setup
    - Multi-agent architecture
    - Ollama integration

- Milestone 2
    - Script generation
    - Storyboard generation

- Milestone 3
    - Image prompt generation

- Milestone 4
    - ComfyUI integration
    - Image generation
    - Image backend abstraction
    - Workflow loading
    - Automatic image saving

---

## Next Milestones

### Milestone 5

Video Assembly

- FFmpeg integration
- Scene sequencing
- Transitions

---

### Milestone 6

Voice Generation

- TTS
- Narration synchronization

---

### Milestone 7

Background Music

- AI generated music
- Ambient effects

---

### Milestone 8

Final Video Rendering

- Narration
- Images
- Music
- Captions

↓

Final MP4

---

# Installation

Clone the repository

```
git clone <repo-url>
```

Create virtual environment

```
python -m venv .venv
```

Install dependencies

```
pip install -r requirements.txt
```

---

# Prerequisites

Install and run:

- Ollama
- ComfyUI
- DreamShaper model

---

# Run

```
python -m app.main
```

Enter a topic

```
Why Your Brain Chooses Comfort Over Success
```

The pipeline will generate:

- Script
- Storyboard
- Image Prompts
- Scene Images

---

# Vision

The long-term vision of THNKBYD is to become an autonomous AI creative studio capable of transforming a single idea into a complete, production-ready educational video with minimal human intervention.