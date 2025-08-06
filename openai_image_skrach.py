import openai  
import io

# הגדרת מפתח ה-API שלך
client =openai.OpenAI()
client.api_key = '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'



# Load your image file
image_path = "1221.png"

# Open the image file in binary mode
with open(image_path, "rb") as image_file:
    image = image_file.convert('RGBA')
    image_data = image.read()

# Convert the image data to a BytesIO object
image_bytes = io.BytesIO(image_data)

# Now you can use the image_bytes in your API call
response = client.images.edit(
    image=image_bytes,
    size="1024x1024",
    prompt="Create skratch image"
)