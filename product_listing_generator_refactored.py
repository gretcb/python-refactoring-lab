import os
import base64
import json

from dotenv import load_dotenv
from openai import OpenAI


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
        raise ValueError("OPENAI_API_KEY not found in .env file")

    return OpenAI(api_key=api_key)


# ---------------------------------------
# IMAGE ENCODING HELPER
# ---------------------------------------

def encode_image_to_base64(image_path):
    """
    Convert an image into a Base64 string.
    """

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    return encoded_image


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
- The title and description must remain consistent with the provided product name.
- Do not describe the product as Hansel and Gretel unless that title is explicitly provided or clearly visible in the image.

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

    return json.loads(cleaned_response.strip())


# ---------------------------------------
# OPENAI LISTING GENERATION HELPER
# ---------------------------------------

def generate_listing(client, prompt, encoded_image):
    """
    Send the product information and image to OpenAI.
    """

    return client.responses.create(
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


# ---------------------------------------
# SINGLE PRODUCT PROCESSING HELPER
# ---------------------------------------

def process_product(client, product):
    """
    Process one product and return its generated listing.
    """

    if not os.path.exists(product["image_path"]):
        raise FileNotFoundError(
            f"Image not found: {product['image_path']}"
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

    response = generate_listing(
        client,
        prompt,
        encoded_image
    )

    parsed_listing = parse_json_response(
        response.output_text
    )

    result = {
        "product_id": product["id"],
        "original_name": product["name"],
        "price": product["price"],
        "category": product["category"],
        "image_path": product["image_path"],
        "listing": parsed_listing
    }

    return result


# ---------------------------------------
# JSON SAVING HELPER
# ---------------------------------------

def save_results_to_json(results, output_path):
    """
    Save the generated product listings to a JSON file.
    """

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(
            results,
            output_file,
            ensure_ascii=False,
            indent=4
        )


# ---------------------------------------
# TEST: Create the OpenAI client
# ---------------------------------------

client = create_openai_client()
print("OpenAI client created successfully!")


# -------------------------------------------------
# TEST: Verify that the OpenAI API connection works
# -------------------------------------------------

# response = client.responses.create(
#     model="gpt-4.1-mini",
#     input="Hello! Tell me one fun fact about Hansel and Gretel fairytale."
# )

# print("\n=== API CONNECTION TEST ===")
# print(response.output_text)


# -------------------------------------------------
# DATASET LOADING TEST
# -------------------------------------------------

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
    print(f"Error: {error}")
    print("Continuing with the local book dataset.")


# -------------------------------------------------
# PRODUCT DATA
# -------------------------------------------------

products_data = [
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

print(f"Products prepared: {len(products_data)}")


# ---------------------------------------
# TEST: Encode one image to Base64
# ---------------------------------------

sample_path = products_data[0]["image_path"]

encoded_image = encode_image_to_base64(sample_path)

print(f"\nEncoded image length: {len(encoded_image)} characters")
print(f"Encoded prefix: {encoded_image[:40]}...")


# -------------------------------------------------
# TEST: Prepare the first product
# -------------------------------------------------

product = products_data[0]

print("\n=== FIRST PRODUCT ===")
print(product)


# -------------------------------------------------
# TEST: Generate the prompt
# -------------------------------------------------

prompt = create_product_listing_prompt(
    product_name=product["name"],
    price=product["price"],
    category=product["category"],
    additional_info=product.get("additional_info")
)

print("\n=== PROMPT PREVIEW ===")
print(prompt[:700])


# -------------------------------------------------
# PROCESS MULTIPLE PRODUCTS
# Generate and parse listings for all products
# -------------------------------------------------

generated_listings = []

for product in products_data:
    print(f"\nProcessing product {product['id']}: {product['name']}")

    try:
        result = process_product(
            client,
            product
        )

        generated_listings.append(result)

        print("Listing generated successfully.")
        print(f"Title: {result['listing']['title']}")

    except FileNotFoundError as error:
        print(f"Image error: {error}")

    except json.JSONDecodeError as error:
        print(f"JSON parsing error: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")


# -------------------------------------------------
# SAVE RESULTS TO JSON
# -------------------------------------------------

output_path = "output/generated_listings.json"

save_results_to_json(
    generated_listings,
    output_path
)

print("\nProcessing completed.")
print(f"Successful listings: {len(generated_listings)}")
print(f"Results saved to: {output_path}")