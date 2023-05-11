# mlops-lyrics-lm

I journal about the progress of this project [here](journal.md)

## Development
Run local
```
bentoml serve service:svc --reload
```

## Production
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
docker run -it --rm -p 3000:3000 lyrics_generator:sivtmnxpwwdkgrq5 serve --production;
```

