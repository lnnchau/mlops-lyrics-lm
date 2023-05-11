# mlops-lyrics-lm

I journal about the progress of this project [here](journal.md)

## Folder structure
```
├── Dockerfile.airflow
├── requirements.airflow.txt
├── docker-compose.airflow.yaml
├── data                            # data for training, managed via DVC
│   ├── readme.md
│   ├── spotify_millsongdata.csv
│   └── spotify_millsongdata.csv.dvc
├── journal.md
├── notebooks                       # .ipynb files for experiment purpose
│   └── gpt_dev.ipynb
└── src                             # model serving code
    ├── bentofile.yaml
    ├── dags                        # define Airflow pipeline
    ├── inference                   # wrapper function for model inference
    ├── requirements.txt
    ├── service.py                  # Bento service file
    └── utils
```

## Model serving
Change directory
```
cd src
```
### Development
Install dependencies
```
pip install -r requirements
```

Run local
```
bentoml serve service:svc --reload
```

### Production
Build: 
```
bentoml build
```

Containerize
```
bentoml containerize lyrics_generator:latest
```
- For Mac users: 
    ```
    bentoml containerize --opt platform=linux/amd64 lyrics_generator:latest
    ```

Serve
```
docker run -it --rm -p 3000:3000 lyrics_generator:latest serve --production;
```

## Run Airflow
To have everything clean, we'll run Airflow inside Docker container.
Build
```
docker compose -f docker-compose.airflow.yaml build
```

Start Airflow
```
docker compose -f docker-compose.airflow.yaml up
```

Clean up
```
docker compose -f docker-compose.airflow.yaml down --volumes --rmi all
```

More on [Running Airflow inside Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) and [Airflow Docker image customization](https://airflow.apache.org/docs/docker-stack/build.html#building-the-image)