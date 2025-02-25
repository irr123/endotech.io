import openai

from .bootstrap import Bootstrap


class Repo:
    def __init__(self, b: Bootstrap):
        self.__b = b
        self.__c = openai.AsyncOpenAI(api_key=b.conf.OPENAI_KEY)

    async def complete(
        self,
        user_prompt: str,
        sys_prompt: str | None = None,
        model: str | None = None,
    ) -> tuple[openai.types.chat.ChatCompletion, None | str]:
        msgs = (
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        )
        if sys_prompt is None:
            msgs = msgs[1:]

        resp: openai.types.chat.ChatCompletion = await self.__c.chat.completions.create(
            messages=msgs,
            model=model or self.__b.conf.OPENAI_MODEL,
            temperature=0.7,
            n=1,
        )

        if resp.choices and len(resp.choices) > 0:
            return resp, resp.choices[0].message.content

        return resp, None
