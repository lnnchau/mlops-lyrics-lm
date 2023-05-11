import bentoml

from inference.wrapper import LyricsGeneratorRunnable

bentoml_model = bentoml.pytorch.get("bigramlm")
lyrics_generator_runner = bentoml.Runner(
    runnable_class=LyricsGeneratorRunnable,
    runnable_init_params={"bentoml_model": bentoml_model})
svc = bentoml.Service("lyrics_generator",
                      runners=[lyrics_generator_runner],
                      models=[bentoml_model])


@svc.api(input=bentoml.io.Text(), output=bentoml.io.JSON())
def generate_lyrics(input_text: str) -> str:
    result = lyrics_generator_runner.generate_lyrics.run(input_text)
    return {
        "res": result
    }
