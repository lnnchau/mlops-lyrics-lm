from pathlib import Path
from datetime import timedelta
from airflow.decorators import task, dag
from airflow.operators.bash import BashOperator
import pendulum


@dag(
    dag_id="serve_workflow",
    schedule_interval=timedelta(minutes=5),
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=["serve", "lyrics-gen"],
)
def serve_workflow_dag():
    @task.branch(
        task_id="branch_task",
        provide_context=True)
    def branch_func(**kwargs):
        ti = kwargs['ti']
        xcom_value = bool(ti.xcom_pull(task_ids="fetch_new_model"))
        if xcom_value is True:
            return "select_model"
        else:
            return None

    @task(
        task_id="fetch_new_model",
        do_xcom_push=True)
    def fetch_new_model():
        from mlflow.tracking.client import MlflowClient

        client = MlflowClient()

        new_model = client.get_latest_versions(
            "BigramLanguageModel", stages=["None"])

        if len(new_model) > 0:
            return True

        return False

    @task(task_id="select_model")
    def select_model():
        """
        Select the best model from new models and production model

        Returns:
            bool: True if there's new model with better metric, False otherwise
        """
        from mlflow.tracking.client import MlflowClient

        client = MlflowClient()

        best_metric, best_version = -1, -1
        model_updated = True    # assume there's no production model

        prod_models = client.get_latest_versions(
            "BigramLanguageModel", stages=["Production"])
        if len(prod_models) > 0:
            prod_model = prod_models[0]

            # if there's production model, `model_updated` is False by default
            # will update to True if there's new model with better metric
            model_updated = False
            best_metric = client.get_metric_history(
                prod_model.run_id, "ppl")[0].value
            best_version = prod_model.version

        new_models = client.get_latest_versions(
            "BigramLanguageModel", stages=["None"])
        for new_model in new_models:
            metric = client.get_metric_history(
                new_model.run_id, "ppl")[0].value

            # if there's no production model, this will always be True
            # if there's production model, this will be True if new model has better metric
            if metric > best_metric:
                best_metric = metric
                best_version = new_model.version
                model_updated = True

        if model_updated:
            client.transition_model_version_stage(
                name="BigramLanguageModel",
                version=best_version,
                stage="Production",
                archive_existing_versions=True,
            )

            return True

        return False

    @task(task_id="import_model")
    def import_model():
        from utils.tokenizer import TokenizerUnpickler
        import mlflow
        import bentoml

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

    # initantiate tasks
    fetch_new_model_task = fetch_new_model()
    select_model_task = select_model()
    import_model_task = import_model()

    build_bento_task = BashOperator(
        task_id="build_bento",
        bash_command="bentoml build -f /opt/airflow/bentofile.yaml /opt/airflow"
    )

    # initantiate branch task
    branch_op = branch_func()

    fetch_new_model_task >> branch_op >> select_model_task >> import_model_task >> build_bento_task


serve_workflow_dag()
