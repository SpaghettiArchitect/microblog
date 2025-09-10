import uuid

import requests
from flask import current_app
from flask_babel import _


def translate(text: str, src_lang: str, dest_lang: str) -> str:
    """Translate text from the source language to the destination language."""
    if (
        "TRANSLATOR_KEY" not in current_app.config
        or not current_app.config["TRANSLATOR_KEY"]
    ):
        return _("Error: the translation service is not configured.")

    key = current_app.config["TRANSLATOR_KEY"]
    endpoint = "https://api.cognitive.microsofttranslator.com"

    path = "/translate"
    constructed_url = endpoint + path

    params = {
        "api-version": "3.0",
        "from": src_lang,
        "to": dest_lang,
    }

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]

    r = requests.post(constructed_url, params=params, headers=headers, json=body)

    if r.status_code != 200:
        return _("Error: the translation service failed.")

    return r.json()[0]["translations"][0]["text"]
