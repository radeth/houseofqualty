from time import sleep

import requests

API_URL = "https://api-inference.huggingface.co/models/timpal0l/mdeberta-v3-base-squad2"
headers = {"Authorization": "Bearer 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"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


output = query({
    "inputs": {
        "question": "Co to jest dom jakosci?",
        "context": "Bedziemy tworzyc dom jakosci"
    },
})
sleep(1)
