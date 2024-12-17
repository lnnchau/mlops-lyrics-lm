
import bentoml
import mlflow

from utils.tokenizer import TokenizerUnpickler


mlflow_model_path = 'models:/BigramLanguageModel/Production'

model = mlflow.pytorch.load_model(
    mlflow_model_path, map_location='cpu')
tokenizer_path = mlflow.artifacts.download_artifacts(
    mlflow_model_path + '/artifacts/tokenizer.pkl')

tokenizer = TokenizerUnpickler(open(tokenizer_path, 'rb')).load()

bentoml.pytorch.save_model(
    name="bigramlm",
    model=model,
    signatures={
        "generate": {
            "batchable": True
        }
    },
    custom_objects={"tokenizer": tokenizer},
)
