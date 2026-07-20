import os
import base64
import json

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIError,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)


# ---------------------------------------
# OPENAI CLIENT HELPER
# ---------------------------------------

def create_openai_client():
    """
    Load the OpenAI API key and create an OpenAI client.
    """

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Check that the .env file exists "
            "and contains OPENAI_API_KEY."
        )

    return OpenAI(api_key=api_key)


# ---------------------------------------
# IMAGE ENCODING HELPER
# ---------------------------------------

def encode_image_to_base64(image_path):
    """
    Convert an image into a Base64 string.
    """

    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        return encoded_image

    except FileNotFoundError as error:
        print("\n=== IMAGE ENCODING ERROR ===")
        print("Function: encode_image_to_base64()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print(f"Image path: {image_path}")
        print(
            "Suggestion: Check that the image exists and that the "
            "file path is correct."
        )
        raise

    except PermissionError as error:
        print("\n=== IMAGE ENCODING ERROR ===")
        print("Function: encode_image_to_base64()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print(f"Image path: {image_path}")
        print("Suggestion: Check the image file permissions.")
        raise


# ---------------------------------------
# PROMPT CREATION HELPER
# ---------------------------------------

def create_product_listing_prompt(
    product_name,
    price,
    category,
    additional_info=None
):
    """
    Create a prompt for generating an optimized product listing.
    """

    prompt = f"""
You are a Senior Creative Copywriter working for a leading international advertising agency.

You are an expert in:
- E-commerce
- SEO
- Digital Marketing
- Web Analytics
- Conversion Rate Optimization (CRO)
- Product Marketing

Your objective is to create product listings that increase customer interest and purchase intent while remaining accurate and trustworthy.

Write for online shoppers scanning product pages. Prioritize clarity, readability and purchase intent.

Assume the customer has only a few seconds to decide whether to keep reading.

Analyze both the provided product information and the product image before writing the listing.

Identify colors, materials, typography, illustrations, packaging, design elements and any other visible characteristics that may help create a more accurate product listing.

Treat each product independently.

Do not reuse information from previous products.

The product name provided below is the primary source of truth.

Use the image only to enrich the description with visible details such as colors, typography, illustrations, layout and design.

If the image and the product name appear inconsistent, prioritize the provided product name and avoid making assumptions.

Product Information:
- Name: {product_name}
- Price: ${price:.2f}
- Category: {category}
{f"- Additional Information: {additional_info}" if additional_info else ""}

Create a product listing that includes:

1. Product Title
- Maximum 60 characters
- Clear, attractive and SEO-friendly

2. Product Description
- Between 120 and 180 words
- Creative but professional
- Persuasive without sounding exaggerated
- Warm, engaging, concise and easy to read
- Highlight benefits, not only features
- Mention only details visible in the image or provided information
- Avoid clichés, excessive hype, forced jokes or overly humorous language
- The title and description must remain consistent with the provided product name
- Do not describe the product as Hansel and Gretel unless that title is explicitly provided or clearly visible in the image

3. Key Features
- Exactly 5 bullet points
- Maximum 90 characters per bullet

4. SEO Keywords
- Between 10 and 15 keywords
- Comma separated
- No repeated keywords

The listing should help customers quickly understand why the product is worth buying while remaining honest and factually accurate.

Use a polished, attention-grabbing tone, but do not make the copy silly, gimmicky or excessively playful.

Return ONLY valid JSON using the following structure:
Do not include markdown, code blocks, explanations or any additional text.

{{
    "title": "...",
    "description": "...",
    "features": [
        "...",
        "...",
        "...",
        "...",
        "..."
    ],
    "keywords": "..."
}}

Do not invent product specifications, authors, publishers, materials, dimensions or features that cannot be confirmed from the image or the provided information.

Never state facts such as edition, publisher, publication date, illustrator or author unless they are clearly visible in the image or explicitly provided as input.

If any information cannot be determined from the image or the provided data, omit it rather than making assumptions.
"""

    return prompt.strip()


# ---------------------------------------
# JSON PARSING HELPER
# ---------------------------------------

def parse_json_response(response_text):
    """
    Convert the model response into a Python dictionary.
    Remove Markdown code blocks if the model includes them.
    """

    cleaned_response = response_text.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]

    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]

    try:
        return json.loads(cleaned_response.strip())

    except json.JSONDecodeError as error:
        print("\n=== JSON PARSING ERROR ===")
        print("Function: parse_json_response()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print(f"Line: {error.lineno}")
        print(f"Column: {error.colno}")
        print(f"Character position: {error.pos}")
        print(
            "Context: The OpenAI response could not be converted "
            "into valid JSON."
        )
        print(
            "Suggestion: Check that the model returned complete JSON "
            "with valid quotes, commas and brackets."
        )
        raise


# ---------------------------------------
# OPENAI LISTING GENERATION HELPER
# ---------------------------------------

def generate_listing(client, prompt, encoded_image):
    """
    Send the prompt and image to OpenAI and return the response text.
    """

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": (
                                f"data:image/jpeg;base64,{encoded_image}"
                            )
                        }
                    ]
                }
            ]
        )

        return response.output_text

    except AuthenticationError as error:
        print("\n=== OPENAI API ERROR ===")
        print("Function: generate_listing()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Context: OpenAI rejected the API credentials.")
        print("Suggestion: Check the OPENAI_API_KEY value in the .env file.")
        raise

    except RateLimitError as error:
        print("\n=== OPENAI API ERROR ===")
        print("Function: generate_listing()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Context: The OpenAI request reached a rate or quota limit.")
        print("Suggestion: Check API quota and retry after a short delay.")
        raise

    except APITimeoutError as error:
        print("\n=== OPENAI API ERROR ===")
        print("Function: generate_listing()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Context: The OpenAI request timed out.")
        print("Suggestion: Check the connection and retry the request.")
        raise

    except APIConnectionError as error:
        print("\n=== OPENAI API ERROR ===")
        print("Function: generate_listing()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Context: The application could not connect to OpenAI.")
        print("Suggestion: Check the internet connection and retry.")
        raise

    except APIError as error:
        print("\n=== OPENAI API ERROR ===")
        print("Function: generate_listing()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Context: OpenAI returned an API error.")
        print("Suggestion: Check the model name, request data and API status.")
        raise

    except Exception as error:
        print("\n=== LISTING GENERATION ERROR ===")
        print("Function: generate_listing()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Context: An unexpected error occurred while generating a listing.")
        print("Suggestion: Review the request inputs and traceback.")
        raise


# ---------------------------------------
# SINGLE PRODUCT PROCESSING HELPER
# ---------------------------------------

def process_product(client, product):
    """
    Coordinate the processing of one product.
    """

    required_fields = [
        "id",
        "name",
        "price",
        "category",
        "image_path"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in product
    ]

    if missing_fields:
        raise ValueError(
            "Missing required product fields: "
            + ", ".join(missing_fields)
        )

    prompt = create_product_listing_prompt(
        product_name=product["name"],
        price=product["price"],
        category=product["category"],
        additional_info=product.get("additional_info")
    )

    encoded_image = encode_image_to_base64(
        product["image_path"]
    )

    response_text = generate_listing(
        client,
        prompt,
        encoded_image
    )

    parsed_listing = parse_json_response(
        response_text
    )

    return {
        "product_id": product["id"],
        "original_name": product["name"],
        "price": product["price"],
        "category": product["category"],
        "image_path": product["image_path"],
        "listing": parsed_listing
    }


# ---------------------------------------
# JSON SAVING HELPER
# ---------------------------------------

def save_results_to_json(results, output_path):
    """
    Save the generated product listings to a JSON file.
    """

    try:
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(
                results,
                output_file,
                ensure_ascii=False,
                indent=4
            )

    except FileNotFoundError as error:
        print("\n=== JSON SAVING ERROR ===")
        print("Function: save_results_to_json()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print(f"Output path: {output_path}")
        print("Suggestion: Check that the destination folder exists.")
        raise

    except PermissionError as error:
        print("\n=== JSON SAVING ERROR ===")
        print("Function: save_results_to_json()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print(f"Output path: {output_path}")
        print(
            "Suggestion: Check that you have permission to write "
            "to this location."
        )
        raise

    except OSError as error:
        print("\n=== JSON SAVING ERROR ===")
        print("Function: save_results_to_json()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print(f"Output path: {output_path}")
        print("Suggestion: Check the output path and available disk space.")
        raise


# ---------------------------------------
# ERROR HANDLING TESTS
# ---------------------------------------

def run_error_handling_tests():
    """
    Run controlled tests for required error scenarios.
    """

    # TEST: Encode a missing image
    print("\n=== TEST: MISSING IMAGE ===")

    try:
        encode_image_to_base64(
            "images/image_that_does_not_exist.png"
        )
    except FileNotFoundError:
        print("Missing image test completed successfully.")

    # TEST: Parse invalid JSON response
    print("\n=== TEST: INVALID JSON RESPONSE ===")

    invalid_json_response = """
{
    "title": "Hansel y Gretel"
    "description": "Illustrated book"
}
"""

    try:
        parse_json_response(invalid_json_response)
    except json.JSONDecodeError:
        print("Invalid JSON test completed successfully.")

    # TEST: Save results to a missing folder
    print("\n=== TEST: INVALID OUTPUT PATH ===")

    try:
        save_results_to_json(
            [{"test": "data"}],
            "folder_that_does_not_exist/test_results.json"
        )
    except FileNotFoundError:
        print("Invalid output path test completed successfully.")


# ---------------------------------------
# PRODUCT DATA
# ---------------------------------------

PRODUCTS_DATA = [
    {
        "id": 1,
        "name": "The Original Folk & Fairy Tales of the Brothers Grimm",
        "price": 34.95,
        "category": "Books",
        "image_path": "images/producto1.png",
        "additional_info": (
            "Collection of original Brothers Grimm fairy tales"
        )
    },
    {
        "id": 2,
        "name": "Hansel y Gretel",
        "price": 24.95,
        "category": "Books",
        "image_path": "images/producto2.png",
        "additional_info": (
            "Illustrated edition adapted by Stephen King "
            "and Maurice Sendak"
        )
    },
    {
        "id": 3,
        "name": "Hansel y Gretel",
        "price": 19.95,
        "category": "Books",
        "image_path": "images/producto3.png",
        "additional_info": (
            "Illustrated edition designed by Agnese Baruzzi"
        )
    }
]


# ---------------------------------------
# MAIN WORKFLOW
# ---------------------------------------

def main():
    """
    Run tests, process all products and save successful listings.
    """

    run_error_handling_tests()

    try:
        client = create_openai_client()
        print("\nOpenAI client created successfully!")

    except ValueError as error:
        print("\n=== OPENAI CLIENT ERROR ===")
        print("Function: create_openai_client()")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Suggestion: Add OPENAI_API_KEY to the .env file.")
        return

    # Optional dataset-loading demonstration from the original lab
    try:
        from datasets import load_dataset
        import pandas as pd

        print("\nLoading Hugging Face dataset...")

        dataset = load_dataset(
            "ashraq/fashion-product-images-small",
            split="train[:10]"
        )

        products_df = pd.DataFrame(dataset)

        print(f"Hugging Face products loaded: {len(products_df)}")
        print(f"Dataset columns: {products_df.columns.tolist()}")

    except Exception as error:
        print("\nCould not load the Hugging Face dataset.")
        print(f"Error type: {type(error).__name__}")
        print(f"Message: {error}")
        print("Continuing with the local book dataset.")

    print(f"Products prepared: {len(PRODUCTS_DATA)}")

    # TEST: Encode one valid image to Base64
    sample_path = PRODUCTS_DATA[0]["image_path"]
    encoded_image = encode_image_to_base64(sample_path)

    print(f"\nEncoded image length: {len(encoded_image)} characters")
    print(f"Encoded prefix: {encoded_image[:40]}...")

    # TEST: Prepare the first product
    first_product = PRODUCTS_DATA[0]

    print("\n=== FIRST PRODUCT ===")
    print(first_product)

    # TEST: Generate the prompt
    prompt = create_product_listing_prompt(
        product_name=first_product["name"],
        price=first_product["price"],
        category=first_product["category"],
        additional_info=first_product.get("additional_info")
    )

    print("\n=== PROMPT PREVIEW ===")
    print(prompt[:700])

    # PROCESS MULTIPLE PRODUCTS
    generated_listings = []

    for product in PRODUCTS_DATA:
        print(
            f"\nProcessing product {product['id']}: "
            f"{product['name']}"
        )

        try:
            result = process_product(
                client,
                product
            )

            generated_listings.append(result)

            print("Listing generated successfully.")
            print(f"Title: {result['listing']['title']}")

        except FileNotFoundError:
            print("Product skipped because its image could not be loaded.")

        except json.JSONDecodeError:
            print("Product skipped because the API response was not valid JSON.")

        except ValueError as error:
            print("\n=== PRODUCT DATA ERROR ===")
            print("Function: process_product()")
            print(f"Error type: {type(error).__name__}")
            print(f"Message: {error}")
            print(f"Product context: {product}")
            print("Suggestion: Check the required product fields.")

        except (
            AuthenticationError,
            RateLimitError,
            APITimeoutError,
            APIConnectionError,
            APIError
        ):
            print("Product skipped because the OpenAI request failed.")

        except Exception as error:
            print("\n=== UNEXPECTED PROCESSING ERROR ===")
            print("Function: main() product loop")
            print(f"Error type: {type(error).__name__}")
            print(f"Message: {error}")
            print(f"Product context: {product}")
            print("Suggestion: Review the traceback and product input.")

    # SAVE RESULTS TO JSON
    output_path = "output/generated_listings.json"

    try:
        save_results_to_json(
            generated_listings,
            output_path
        )

    except OSError:
        print("Results could not be saved.")
        return

    print("\nProcessing completed.")
    print(f"Successful listings: {len(generated_listings)}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
