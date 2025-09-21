FROM python:3.11-slim

# Basic tools & wheels cache improvements
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential && rm -rf /var/lib/apt/lists/*

# Prevent interactive tzdata prompts and speed up pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_COLOR=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Nothing copied yet — build stays static; we copy code at run-time build step
