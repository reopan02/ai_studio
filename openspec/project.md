# AI Studio Project

## Overview

AI Studio is a full-stack application for AI-powered e-commerce product image generation. It combines a FastAPI backend with a Vue 3 frontend, using Supabase for authentication and database.

## Architecture

- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: Vue 3 + TypeScript + Vite MPA
- **Database**: PostgreSQL via Supabase
- **Auth**: Supabase Auth (JWT-based)
- **LLM**: StructLLM with Gemini/GPT-4V for vision analysis

## Modules

### Implemented

1. **Product Library (Module 1)**: Upload product images with AI attribute recognition
2. **E-commerce Image Generation**: Wizard-based product image generation
3. **Video Generation**: AI video generation with multiple models
4. **Storage Management**: User file storage and quota management

### Proposed

1. **Batch Prompt Generation**: Generate prompts from reference images/text for product image generation

## Key Directories

```
ai_studio/
├── app/                    # Backend FastAPI application
│   ├── api/v1/            # API endpoints
│   ├── clients/           # LLM and external API clients
│   ├── core/              # Core services and utilities
│   ├── models/            # Database models and schemas
│   └── static/            # Static files and uploads
├── frontend/              # Vue 3 frontend
│   └── src/pages/         # MPA page components
├── infra/                 # Infrastructure (Supabase)
└── openspec/              # Specifications and proposals
    ├── changes/           # Change proposals
    └── specs/             # Stable specifications
```

## Conventions

- Chinese UI text for user-facing content
- English for code comments and documentation
- StructLLM for all structured LLM output
- Supabase PostgREST for direct DB access from frontend
- Backend API for file operations and LLM calls
