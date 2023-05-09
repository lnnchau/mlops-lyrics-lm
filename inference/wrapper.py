import torch
import bentoml

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LyricsGenerator:
    def __init__(self, model_name="bigramlm:latest"):
        bento_model = bentoml.pytorch.get(model_name)

        self.model = bentoml.pytorch.load_model(model_name)
        self.model.to(device)
        self.model.eval()

        self.tokenizer = bento_model.custom_objects["tokenizer"]

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

    def __init__(self):
        # load the model instance
        self.generator = LyricsGenerator()

    @bentoml.Runnable.method(batchable=False)
    def generate_lyrics(self, input_data: str) -> str:
        return self.generator.get_lyrics(input_data)
