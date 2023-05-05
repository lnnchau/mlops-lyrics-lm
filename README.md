# mlops-lyrics-lm

## Goal: Build CI/CD pipeline for a ML project.

I've been hyping about MLOps a few years ago, but I'm so ashamed to say that I was too lazy to get my hands dirty. Every time I planned to start a side project, I got too overwhelmed by the influx of tools, frameworks, documentations and tutorials that I was finally drowned before I even started. This time is no difference. However, I try to break down things. There are two scenarios where you need to automate the model deployment:
- The data scientist updates the code and weights for the model
- The production detects a data drift / new data => triggers the ML pipeline

In this project, I aim to tackle each of them.

## Scenario 1: The data scientist updates the code and weights for the model 
- [x] Reimplement bigram model from this with Spotify dataset
- [x] Implement PPL metric

### 5/5/2023
- [x] Set up
    - [x] Git (this)
    - [x] DagsHub (connect with this git)
    - [x] DVC
        - as suggested in the documentation, should install in a `Python3.8+` virtual env (you gotta know why)
        - add the training data ([explanation](https://dvc.org/doc/start/data-management/data-versioning#add-click-to-get-a-peek-under-the-hood))
- [x] Reimplement bigram model from this with Spotify dataset
    - Start with Google Colab first for the sake of GPU resources
    - Link Google Colab with this repo
- [x] Implement PPL metric
    - Reference
        - https://web.stanford.edu/~jurafsky/slp3/3.pdf (original formula)
        - https://huggingface.co/docs/transformers/perplexity (to handle inf when taking product of small values)
    - As a sanity test, I use the [bigram model with attention](https://www.youtube.com/watch?v=kCc8FmEb1nY) to compare with PPL from simple bigram model
