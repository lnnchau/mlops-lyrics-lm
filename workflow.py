MODEL_PATH_PROD = "models:/BigramLanguageModel/Production"


def choose_best_model():
    from mlflow.tracking.client import MlflowClient

    client = MlflowClient()

    new_model = client.get_latest_versions(
        "BigramLanguageModel", stages=["None"])[0]
    metric = client.get_metric_history(new_model.run_id, "ppl")[0].value

    current_models = client.get_latest_versions(
        "BigramLanguageModel", stages=["Production"])
    if len(current_models) > 0:
        current_model = current_models[0]

        max_metric = (
            client.get_metric_history(current_model.run_id, "ppl")[0].value
            if current_model
            else 0
        )

        if metric < max_metric:
            return

        # archive current production model
        client.transition_model_version_stage(
            name="BigramLanguageModel",
            version=current_model.version,
            stage="Archived",
        )

    # move new model to production
    client.transition_model_version_stage(
        name="BigramLanguageModel",
        version=new_model.version,
        stage="Production",
    )


def import_model(mlflow_model_path):
    from utils.tokenizer import TokenizerUnpickler
    import mlflow
    import bentoml

    model = mlflow.pytorch.load_model(mlflow_model_path, map_location='cpu')
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
