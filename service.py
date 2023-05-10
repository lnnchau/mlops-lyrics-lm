import bentoml

from inference.wrapper import LyricsGeneratorRunnable

lyrics_generator_runner = bentoml.Runner(LyricsGeneratorRunnable)
svc = bentoml.Service("lyrics_generator", runners=[lyrics_generator_runner])


@svc.api(input=bentoml.io.Text(), output=bentoml.io.JSON())
def generate_lyrics(input_text: str) -> str:
    result = lyrics_generator_runner.generate_lyrics.run(input_text)
    return {
        "res": result
    }
