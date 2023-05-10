# mlops-lyrics-lm

## Goal: Build CI/CD pipeline for a ML project.

I've been hyping about MLOps a few years ago, but I'm so ashamed to say that I was too lazy to get my hands dirty. Every time I planned to start a side project, I got too overwhelmed by the influx of tools, frameworks, documentations and tutorials that I was finally drowned before I even started. This time is no difference. However, I try to break down things. There are two scenarios where you need to automate the model deployment:
- The data scientist updates the code and weights for the model
- The production detects a data drift / new data => triggers the ML pipeline

In this project, I aim to tackle each of them.

## Scenario 1: The data scientist updates the code and weights for the model 
- [x] Reimplement bigram model from this with Spotify dataset
- [x] Implement PPL metric
- [x] Log model metrics with MLFlow
- [x] Register model to MLFlow
- [x] Use DagsHub as MLFlow experiment store
- [x] Deploy the model with BentoML successfully on local
- [] Trigger deployment on new registered model

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


### 6/5/2023
It seems to work (for now), so today the goal is to learn `mlflow`
- [x] Use MLFlow to log on Google Colab
    - [x] Config
    - [x] Metric: step loss, final PPL
    - [x] Log model / register model
- [x] Make sure I can use that saved model

I really want to only use `mlflow` end-to-end but the its model serving seems not be flexible for untraditional tasks like text-generation. List down what the API should do
- Input: first letter / first word (whatever the use case to be decided later)
- What is done behind the scene:
    - Encode the context to input ids
    - Feed the input ids into the model
    - Decode the generated text
- Output: return the generated text

So basically what I need is a tool where I can define the workflow in a script and deploy the script. I guess `mlflow` doesn't have that flexibility (or maybe I didn't read the docs that thoroughly). Well, as I'm writing, I realize I should have save encode and decode function as artifacts too! To do this, I'll wrap the vocab, encoder, and decoder into a class called Tokenizer (inspired from HuggingFace 🤗)
- [x] Wrap vocab, encode and decoder into tokenizer
- [x] Update the code to use tokenizer

Hmm there's some issues when I'm trying to call import model from BentoML... Will findout sometime later

### 8/5/2023
Well turns out it was just naming issues. Should not name BentoML model with dash symbol `-`
Here's the goal for today:
- [x] Deploy the model with BentoML successfully on local

Currently, our inference model has two components:
- Bigram model
- Tokenizer

In order to reuse tokenizer in the inference code, I've saved it as artifacts via `pickle`. However, now that I realize `pickle` brings more trouble
1. `pickle` won't reconstruct the instance, but need access to the class to load the pickled information in.
2. The class `pickle` requires must be from `__main__`, which is `__main__.<ClassName>`, but of course the `ClassName` cannot be guaranteed to always be in `__main__` module.

More details can be found [here](https://stackoverflow.com/questions/27732354/unable-to-load-files-using-pickle-and-multiple-modules).

I will put this into the backlog to get rid of the unnecessary complexity. For now, please find the workaround of this in `inference/utils.py`. One more important thing to note is that it is highly recommended to have the same Python version for both the experiment and deployment environment.

### 9/5/2023
The more I read the code in `wrapper`, the more I feel something's off.
- I first attempted to import the registered model from `mlflow` to `bentoml`. While the model was registered with `mlflow.pytorch`, `bentoml` only sees it as a PyFunc object only and hence, doesn't accept any custom function other than `predict`.
- Therefore, one workaround is to use the model pulled directly from `mlflow`. We save it to `bentoml` only because it's part of the workflow.
- Here's the thing, so what's the point of using `bentoml` then? It's very inefficient when:
    1. We pull the model from `mlflow` and import it to `bentoml`
    2. We pull the model from `mlflow` again when serving
- One solution I could thing of right now is: When saving the model to `bentoml`, I'll pull the model from `mlflow` and then save it using `bentoml.pytorch`. A huge upside of this solution is that `bentoml` would accept any custom functions of a `pytorch` object. It should be demonstrated in `import_model` function in `workflow.py`. Btw this file would store the functions used for automated workflow later.

### 10/5/2023
- Set up Airflow
    - overview: deploy new model if there's a new registered model
    - fetch_new_model_task >> branch_op >> select_model_task >> import_model_task >> build_bento_task >> deploy_task
    - approach:
        - use airflow inside docker container
        - deploy to aws lambda
    - blocker: permission denied when trying to create directory for new model
