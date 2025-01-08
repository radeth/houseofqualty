import json

from openai import OpenAI

client = OpenAI()


def get_req_parm_matrix_from_ai(product_name, product_description, client_requirements, technical_parameters):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "text": "Generowanie matrycy zależności pomiędzy parametrami technicznymi a wymaganiami klientów w celu wsparcia procesu tworzenia drzewa jakości QFD. Dostarczę nazwę produktu, opis produktu, wymagania klientów i parametry techniczne.\n\n# Steps\n\n1. **Zdefiniuj Wymagania Klientów:** Ustal listę wymagań klientów, które produkt ma spełniać.\n2. **Zidentyfikuj Parametry Techniczne:** Określ kluczowe parametry techniczne, które mogą wpływać na spełnienie wymagań klientów.\n3. **Wykorzystaj Nazwę i Opis Produktu:** Zastosuj dostarczoną nazwę i opis produktu, aby lepiej zrozumieć kontekst i wyodrębnić istotne parametry techniczne oraz wymagania klientów.\n4. **Określ Zależności:** Zanalizuj, w jaki sposób każdy parametr techniczny wpływa na każde wymaganie klienta. Użyj skali, np.1 (słaba zależność), 3(średnia zależność), 9 (silna zależność).\n5. **Zbuduj Matrycę:** Skonstruuj matrycę zależności, umieszczając parametry techniczne na jednej osi, a wymagania klientów na drugiej.\n\n# Output Format\n\nMatryca zależności prezentowana w formacie tabeli, gdzie wiersze reprezentują parametry techniczne, a kolumny wymagania klientów. Każda komórka zawiera wartość zależności.\n\n# Examples\n\nPrzykład matrycy (użyj placeholderów dla rzeczywistych danych):\n- **Nazwa Produktu:** [Nazwa]\n- **Opis Produktu:** [Opis]\n- **Wymagania Klientów:** [W1, W2, W3]\n- **Parametry Techniczne:** [P1, P2, P3]\n\n|              | W1 | W2 | W3 |\n|--------------|----|----|----|\n| **P1**       |  1 |  1 |  3 |\n| **P2**       |  3 |  1 |  1 |\n| **P3**       |  9 |  3 |  1 |\n\n# Notes\n\n- Upewnij się, że wszystkie istotne wymagania i parametry są uwzględnione.\n- Wykorzystuj dostarczoną nazwę i opis produktu, aby zapewnić pełne zrozumienie kontekstu.\n- Skoncentruj się na dokładnym określeniu stopnia wpływu, aby matryca była jak najbardziej użyteczna.\n- W przypadku skomplikowanych produktów możliwe jest zastosowanie dodatkowych kroków analizy i walidacji wyników.",
                        "type": "text"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Product Name: {product_name} Product Description: {product_description} Client Requirements: {client_requirements} Technical Parameters: {technical_parameters}\n"
                    }
                ]
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "dependency_matrix",
                "schema": {
                    "type": "object",
                    "required": [
                        "product_name",
                        "product_description",
                        "technical_parameters",
                        "client_requirements",
                        "dependency_matrix"
                    ],
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "The name of the product."
                        },
                        "dependency_matrix": {
                            "type": "array",
                            "description": "A matrix indicating the dependency between technical parameters and client requirements.",
                            "items": {
                                "type": "array",
                                "description": "A single row of dependencies corresponding to a technical parameter.",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "1",
                                        "3",
                                        "9"
                                    ]
                                }
                            }
                        },
                        "client_requirements": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "A list of requirements specified by the clients."
                        },
                        "product_description": {
                            "type": "string",
                            "description": "A description of the product."
                        },
                        "technical_parameters": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "A list of technical parameters relevant to the product."
                        }
                    },
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    data = json.loads(response.choices[0].message.content)
    return data['dependency_matrix']


def get_openai_suggestions(product_name, product_description, client_requirements, technical_parameters):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "text": "Generowanie matrycy zależności pomiędzy parametrami technicznymi a wymaganiami klientów w celu wsparcia procesu tworzenia drzewa jakości QFD. Dostarczę nazwę produktu, opis produktu, wymagania klientów i parametry techniczne.\n\n# Steps\n\n1. **Zdefiniuj Wymagania Klientów:** Ustal listę wymagań klientów, które produkt ma spełniać.\n2. **Zidentyfikuj Parametry Techniczne:** Określ kluczowe parametry techniczne, które mogą wpływać na spełnienie wymagań klientów.\n3. **Wykorzystaj Nazwę i Opis Produktu:** Zastosuj dostarczoną nazwę i opis produktu, aby lepiej zrozumieć kontekst i wyodrębnić istotne parametry techniczne oraz wymagania klientów.\n4. **Określ Zależności:** Zanalizuj, w jaki sposób każdy parametr techniczny wpływa na każde wymaganie klienta. Użyj skali, np.1 (słaba zależność), 3(średnia zależność), 9 (silna zależność).\n5. **Zbuduj Matrycę:** Skonstruuj matrycę zależności, umieszczając parametry techniczne na jednej osi, a wymagania klientów na drugiej.\n\n# Output Format\n\nMatryca zależności prezentowana w formacie tabeli, gdzie wiersze reprezentują parametry techniczne, a kolumny wymagania klientów. Każda komórka zawiera wartość zależności.\n\n# Examples\n\nPrzykład matrycy (użyj placeholderów dla rzeczywistych danych):\n- **Nazwa Produktu:** [Nazwa]\n- **Opis Produktu:** [Opis]\n- **Wymagania Klientów:** [W1, W2, W3]\n- **Parametry Techniczne:** [P1, P2, P3]\n\n|              | W1 | W2 | W3 |\n|--------------|----|----|----|\n| **P1**       |  1 |  1 |  3 |\n| **P2**       |  3 |  1 |  1 |\n| **P3**       |  9 |  3 |  1 |\n\n# Notes\n\n- Upewnij się, że wszystkie istotne wymagania i parametry są uwzględnione.\n- Wykorzystuj dostarczoną nazwę i opis produktu, aby zapewnić pełne zrozumienie kontekstu.\n- Skoncentruj się na dokładnym określeniu stopnia wpływu, aby matryca była jak najbardziej użyteczna.\n- W przypadku skomplikowanych produktów możliwe jest zastosowanie dodatkowych kroków analizy i walidacji wyników.",
                        "type": "text"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Product Name: {product_name} Product Description: {product_description} Client Requirements: {client_requirements} Technical Parameters: {technical_parameters}\n"
                    }
                ]
            },
        ],
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    data = json.loads(response.choices[0].message.content)
    return data['dependency_matrix']

