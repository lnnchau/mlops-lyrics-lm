
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
- [x] Schedule pipeline to package serving code for newly registered model

### Backlog
- [] Keep only code files in `src`
- [] Get rid of `Tokenizer` pickle. Only pickle the vocab

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
Today's goal is to setup an Airflow for this repo.
- Overview: deploy new model if there's a new registered model
- Workflow:
    1. Fetch new model version: This task checks if there's any new registered model. If yes, the pipeline continues
    2. Select model: For now, this task compare the PPL (metric) of new models and existing production model (if any) to find the version with the best score
    3. Import model: This task imports selected model to BentoML
    4. Build Bento: This task builds a production-ready Bento. Bento 🍱 is a file archive with all the source code, models, data files and dependency configurations required for running a user-defined bentoml. Service, packaged into a standardized format.
    5. Deploy: Deploy to AWS Lambda
- Current approach:
    - Run Airflow locally, inside Docker container
- Issue: permission denied when trying to create directory for new model
- workaround: set the permission of `~/bentoml` to 777 (which sounds not so right)
- Issue: BentoML couldn't find the file

Just a bit of a rant. Maybe I'm a true real morning person. It's not even 10PM now yet I'm keeping doing wacky stuffs -.-

### 11/5/2023
- Had way too many problems trying to package everything via BentoML. Should always remeber to specify `models` param when initiate the service. It's optional param but very important since it lets BentoML know which model to package
- It seems deploying to AWS Lambda is not feasible, so for now the pipeline would be as follows:
    1. Fetch new model version: This task checks if there's any new registered model. If yes, the pipeline continues
    2. Select model: For now, this task compare the PPL (metric) of new models and existing production model (if any) to find the version with the best score
    3. Import model: This task imports selected model to BentoML
    4. Build Bento: This task builds a production-ready Bento. Bento 🍱 is a file archive with all the source code, models, data files and dependency configurations required for running a user-defined bentoml. Service, packaged into a standardized format. The built Bento would be saved in a mounted volume for later use.
- [x] Documentation
    - [x] Serve locally with BentoML
    - [x] Airflow
    - [x] Workflow
- For tomorrow, I think I'd get back to the modelling part. Would like to see the code still works if more complexities are added to the model.

### 20/5/2023
As anticipated, more problems are encountered as I am adding complexities to the model. Most of them lies in the device mismatch when trying to save and load the model. I made use of Google Colab for GPU power and run inference on CPU since my local machine does not have a GPU.

I have trouble loading the model on my local machine. I found this in the model architecture code while debugging and I think this might be the problem
```
pos_emb = self.position_embedding_table(torch.arange(T, device=device)) # (T,C)
```
Currently, `device` is a global variable. Its value is `cuda` on Colab but should be `cpu` on local. I should make this variable configurable. Well actually I must do that to conform to the workflow I defined earlier. However, I, half lazy half impatient, wanted to see it works first, so I kept the original code. I guess I gotta get my hands dirty this time.

One more thing about that line of code. As you can see below, `idx` is already brought to the compatible device before feeding into the model. Assigning device logic is done outside of the model. Meanwhile, the original has assigning device logic done both inside and outside of the model code.
``` 
def forward(self, idx, targets=None):
    B, T = idx.shape

    # idx and targets are both (B,T) tensor of integers
    tok_emb = self.token_embedding_table(idx) # (B,T,C)
    pos_emb = self.position_embedding_table(torch.arange(T, device=device)) # (T,C)
```
We know for sure that `torch.arange(T, device=device)` would have the same device with idx, so changing the device declaration to `device=idx.device` should be good for now. While this is the solution to our problem, I still reorganize the parameter configurations as mentioned above.

Update... That does solve the problem. Besides that, I also encapsulate the training code into a class called Trainer (inspired by PyTorch Lightning)