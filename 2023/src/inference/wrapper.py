import torch
import bentoml

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LyricsGenerator:
    def __init__(self, bentoml_model: bentoml.Model):
        self.model = bentoml.pytorch.load_model(
            bentoml_model.tag, device_id=device)
        self.tokenizer = bentoml_model.custom_objects["tokenizer"]

    def get_lyrics(self, start_phrase, max_new_tokens=2000):
        start_phrase_as_ids = self.tokenizer.encode(start_phrase.lower())
        context = torch.tensor(start_phrase_as_ids,
                               dtype=torch.long, device=device).reshape(1, -1)

        output_tokens = self.model.generate(
            idx=context, max_new_tokens=max_new_tokens)[0].tolist()

        return self.tokenizer.decode(output_tokens)


class LyricsGeneratorRunnable(bentoml.Runnable):
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self, bentoml_model: bentoml.Model):
        # load the model instance
        self.generator = LyricsGenerator(bentoml_model)

    @bentoml.Runnable.method(batchable=False)
    def generate_lyrics(self, input_data: str) -> str:
        return self.generator.get_lyrics(input_data)
