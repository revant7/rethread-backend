from django.core.management.base import BaseCommand
from home.models import Product
import google.generativeai as genai
import time

# Configure your API key
genai.configure(api_key="AIzaSyCDXzbva2AnQlWbKXUDhYR2FRAFFXOOYGA")


def generate_response(prompt, model_name="gemini-2.0-flash-lite"):
    """Generates a response using the Gemini API."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else None
    except Exception as e:
        print(f"Error generating response: {e}")
        return None


class Command(BaseCommand):
    help = "Add Description of Products in batches of 5"

    def handle(self, *args, **options):
        products = Product.objects.all()  # Fetch products with no description
        batch_size = 5

        for i in range(0, len(products), batch_size):
            batch = products[i : i + batch_size]  # Get a batch of 5 products
            product_names = [p.name for p in batch]  # Extract product names

            prompt = f"""
            Write a real-world detailed product description of the given products in this format, separated by ":::" for each product:
            
            (Generate original content suitable for an e-commerce website; do not take data directly from any website.)

            Format:- "

            Highlights: 

            Description: 

            Specifications: 

            Features: 
            "
            Products: {', '.join(product_names)}
            """

            response = generate_response(prompt)

            if response:
                descriptions = response.split(
                    ":::"
                )  # Split descriptions assuming they are separated by double newlines

                for product, desc in zip(batch, descriptions):
                    product.description = desc.strip()
                    product.save()

                print(f"{i + len(batch)} products updated.")
            else:
                print(
                    f"Failed to generate descriptions for batch {i // batch_size + 1}."
                )

            time.sleep(1.5)  # Avoid exceeding API rate limits


# Example with a model that can handle images.
# requires an image, and a model that can handle images.
# from PIL import Image
# import requests
# from io import BytesIO

# def generate_response_with_image(prompt, image_url, model_name="gemini-pro-vision"):
#     """Generates a response using the Gemini API with an image."""
#     try:
#         model = genai.GenerativeModel(model_name)
#         response = model.generate_content([prompt, genai.Part.from_uri(image_url, mime_type="image/jpeg")]) #ensure mime type is correct.
#         return response.text
#     except Exception as e:
#         return f"An error occurred: {e}"

# image_url = "URL_TO_YOUR_IMAGE" #replace with a real image url.
# prompt4 = "Describe this image."
# response4 = generate_response_with_image(prompt4, image_url)
# print(response4)
