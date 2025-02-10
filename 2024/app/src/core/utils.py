from pydantic import BaseModel, Field

format_response_prompt = "The value of structured response object should always be parsed directly from LLM's response without any modification"


class Response(BaseModel):
    answer: str = Field(description="Response content from LLM")
    mp3_fp: str = Field(description="Audio file path. Accept extensions: .mp3")


def get_response_format() -> BaseModel:
    return Response


def get_format_response_prompt() -> str:
    return format_response_prompt
