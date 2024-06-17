# MatchCenterAI API

This repository houses the MatchCenterAI API, an Artificial Intelligence-powered system designed to produce summaries and suggestions based on the events and data of Feyenoord football matches. It contains three packages, of which two are dependencies of the matchcenterai package. It's built using [Nix](https://nixos.org/), but Nix is not required for building.

## Features
AI-powered Summarizer: Generates summaries of football matches based on structured data.
Suggestions: Provides suggestions for content creation based on match events and data.
API: API build using [FastAPI](https://fastapi.tiangolo.com/) and ran using [Uvicorn](https://www.uvicorn.org/) that exposes the functionalities to external projects.


## Prerequisites
If using Nix, use Nix version 2.4 or later
For building with setuptools directly, ensure ffmpeg is installed for the summarizer library.


## Installation

When you're using setuptools, ensure ffmpeg is installed as it is a requirement for the summarizer library. Nix will do this for you.

### Building with Nix

From the root directory of the project, run:

    nix build --experimental-features="nix-command flakes"


### Building with setuptools

Navigate to the project directory and install the dependencies by running

    pip install -r requirements.txt


## Usage

Start the server by running:

    python3 run.py


The server will start on the default port, and the API endpoints will be accessible for use.
