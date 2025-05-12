from openai import OpenAI
import base64
import requests
from PIL import Image
import os


# OpenAI API Key
api_key = "PUT_YOUR_API_KEY_HERE"

# Collector name
collector = "COLLECTORS_NAME"

# Replace 'root_directory' with the path to the root directory you want to scan
root_directory = '/mnt/d/B3A'

def process_images(root_directory):
    for subpath in sorted(os.listdir(root_directory)):
        scans_dir = os.path.join(root_directory, subpath, 'scans')
        front_image_path = os.path.join(scans_dir, '1_front.jpg')
        back_image_path = os.path.join(scans_dir, '2_back.jpg')
        combined_image_path = os.path.join(scans_dir, 'front_and_back.jpg')
        output_path = os.path.join(scans_dir, 'output.json')

        # Check if output file already exists
        if os.path.exists(output_path):
            print(f"Output file {output_path} already exists. Skipping...")
            continue

        if os.path.exists(front_image_path) and os.path.exists(back_image_path):
            print(f"Processing images: {front_image_path} and {back_image_path}")
            
            # Open the front and back images
            front_image = Image.open(front_image_path)
            back_image = Image.open(back_image_path)

            # Get the dimensions of the images
            front_width, front_height = front_image.size
            back_width, back_height = back_image.size

            # Create a new image with width equal to the sum of both images' widths
            # and height equal to the maximum height of both images
            combined_width = front_width + back_width
            combined_height = max(front_height, back_height)

            # Create a new blank image with the combined dimensions
            combined_image = Image.new("RGB", (combined_width, combined_height))

            # Paste the front image on the left
            combined_image.paste(front_image, (0, 0))

            # Paste the back image on the right
            combined_image.paste(back_image, (front_width, 0))

            # Save the combined image
            combined_image.save(combined_image_path)

            print(f"Combined image saved as {combined_image_path}")
            encode_image(combined_image_path, output_path)

        else:
            print(f"Image paths do not exist: {front_image_path} or {back_image_path}")

# Function to encode the image
def encode_image(image_path, output_path):
    with open(image_path, "rb") as image_file:
        send_image_to_openai(image_path, base64.b64encode(image_file.read()).decode('utf-8'), output_path)

def send_image_to_openai(image_path, base64_image, output_path):
    # Identifiers
    path_parts = image_path.split(os.sep)
    BINDER = path_parts[-4]  # Assuming the binder is the third from last part of the path
    IDENTIFIER = path_parts[-3]  # Assuming the identifier is the second from last part of the path

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
Attached is an image showing the front (left) and back (right) sides of an historic postcard. DESCRIBE USING ALL OF THE FOLLOWING (BUT LEAVE BLANK IF NOT KNOWN, **do not put in placeholders like unknown, not applicable, none identified). Use contextual clues like automobiles and clothing styles to help estimate date of creation. respond formatted as JSON.


Do not leave any fields out, especially identifier.

Complete: Yes
Title: Either OCRed text from the front (without square brackets) or a short description you write (placed in square brackets). Do not put OCRed text in square brackets.
Description: Your description of the image on the front card. Do not use flowery prose like, "It provides a glimpse into early 20th-century farming techniques." Do not use information from the title to augment your description. The description should only contain information that can be verified from the content of the image.
Street View: leave blank
Photographer: The photographer, if possible.
Photography Studio: The photography studio, if possible.
Sender: If the card was sent by someone, then this is their name.
Recipient: If the card was sent to someone, then this is the recipient's name.
Recipient Address: If the card was sent to someone, then their address.
Portrait Subject: If the picture on the front is of a person, their name.
Annotation: Additional notes or annotations on the card, after the card's main use (by collectors, etc.)
Message: Transcription of any message written on the card. Do not try to preserve layout, particularly do not use \\n.
Postal Data: Postmarks, postage stamps, and cancellation stamps. The lowest digits on a postmarks are typically the year either four digit or two. E.g., "Postmarks: CITY PROV. MMDD YY (or YYYY); Postage: [describe stamp]; [mention special advertising stamps]"
Publisher: The publisher of the postcard.
Publisher Location: Location of the publisher.
Printer Location: Location of the printer.
Serial Number: Serial number, if applicable.
Date Mailed: Date the postcard was mailed. Use YYYY-MM-DD format. Do not use the square brackets here. This should be learned from the postmark, not a handwritten date in the message section.
Physical Description: Physical description of the postcard. Estimate dimensions of the postcard based on 600dpi scan, give results in mm. Do not mention that it is based on the scan resolution.
Identifier: {IDENTIFIER} 
Language: Language of the written message on the postcard.
Historical Names: Historical names (famous people, former names of buildings or places, etc.) associated with the postcard.
Signs and Banners: Descriptions of signs and banners in the image. Titles of the postcard are not included. Sign must be part of photo. Do all that you can recognize. Signs cannot be on the back of the card.
Subject: Subjects of the photo using TGM controlled vocabulary, semicolon separated, with first letter of the first word in each subject capitalized. Note that ampersands are used instead the full word "and", the term is "Churches" not "Church buildings", and that there is no term "Streetcars" rather one uses "Street railroads" similarly, it isn't "Railway cars" but rather "Railroad cars". "Stairways" is used while "Staircases" is not. "Bands" is used, "Bands (Music)" is not. "Comic books" is used, "Comic books & strips" is not.  Note that related terms are often combined, it's not "City halls" but it is "City & town halls", if you have the functionality to verify that the entries are actually TGM terms then do so.
Geography: Geographic coverage of the postcard like "Downtown, Winnipeg" or "Exchange District, Winnipeg". This is only for when there are photos or illustrations of actual places. It is not enough for a card to be titled, "Winnipeg," for it to get an entry here.
Subject Address: Address of the subject like 123 Main Street, Winnipeg, Manitoba, Canada, H0H 0H0. This is only for when there are photos or illustrations of actual places. It is not enough for a card to be titled, "Winnipeg," for it to get an entry here.
Geographic Coordinates: latitude and longitude of the subject. This is only for when there are photos or illustrations of actual places. It is not enough for a card to be titled, "Winnipeg," for it to get an entry here.
Date Range: The earliest the photo could have been taken to the latest. Use postal information (must be younger than any dates stamped or written on card), clothing and automobile styles, and the presence of a building or combination of buildings.
All Search Years: A semicolon-separated list of all years in the date range. E.g., 1901-1903 becomes 1901; 1902; 1903
Type: Still image
Format: Postcard
Collector: Martin Berman
Usage Statement: Public domain
Digital Publisher: Winnipeg Public Library
Binder: {BINDER}
Type: Still image
Format: Postcard
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000  # Increased the max_tokens value
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()  # Convert response to JSON
    print(response_json) # Print
    # Check if the response contains 'choices' and it's not empty
    if 'choices' in response_json and response_json['choices']:
        content = response_json['choices'][0]['message']['content']
        cleaned_content = content.strip('```json').strip()

        with open(output_path, "w") as file:
            file.write(cleaned_content)
        print(f"Content written to {output_path}")
    else:
        print("No valid response received from OpenAI API")


process_images(root_directory)
