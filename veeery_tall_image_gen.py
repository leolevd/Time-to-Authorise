# The piece of code that generates the Far Lands image in the far lands ending.

# Yeah this is ai generated....
# but hey, I spend quite a bit of time on making this work and look good
# So I guess it counts.


import base64
import io
import requests

from PIL import Image



API_KEY = "Hack Club API Key Goes Here"

URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

MODEL = "google/gemini-3.1-flash-image-preview-20260226"

SEGMENTS = 4

OVERLAP_PERCENT = 0.10

PROMPT = """
Minecraft Far Lands at an enormous distance from the origin.

IMPORTANT COMPOSITION:

Create a STRICTLY VERTICAL, PORTRAIT-ORIENTED LANDSCAPE.

The image must read from TOP TO BOTTOM.

The long dimension of the image represents vertical distance
through the Minecraft world.

The terrain extends downward through the image.

Use a normal upright Minecraft perspective.

DO NOT rotate the scene sideways.
DO NOT create a horizontal panorama.
DO NOT make the landscape flow from left to right.
DO NOT rotate the camera 90 degrees.

The world is an enormous corrupted Far Lands landscape.

Massive distorted cliffs,
gigantic jagged mountains,
impossible terrain formations,
floating fragments,
extreme terrain distortion,
broken terrain,
strange geometric formations.

Minecraft-inspired voxel aesthetic,
detailed blocky terrain,
natural Minecraft-like lighting.

Dark atmospheric sky,
distant fog,
mysterious and surreal atmosphere.

The terrain should feel enormous and geographically continuous.

No UI.
No text.
No characters.
No buildings.
No interface.
"""

def image_to_data_url(image):
    buffer = io.BytesIO()
    image.save(
        buffer,
        format="JPEG",
        quality=90
    )
    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

def get_bottom_overlap(image):
    overlap_height = int(
        image.height * OVERLAP_PERCENT
    )
    overlap_height = max(
        overlap_height,
        1
    )
    top = image.height - overlap_height
    return image.crop(
        (
            0,
            top,
            image.width,
            image.height
        )
    )

def extract_image(data):
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError):
        print()
        print("Unexpected API response:")
        print(data)
        raise RuntimeError(
            "Could not find choices[0].message."
        )
    image_list = message.get("images")
    if not image_list:
        print()
        print("API did not return message.images.")
        print()
        print("Full response:")
        print(data)
        raise RuntimeError("No images returned by API.")
    image_data = None
    for item in image_list:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "image_url":
            continue
        image_url = item.get("image_url")
        if not isinstance(image_url, dict):
            continue
        image_data = image_url.get("url")
        if image_data:
            break
    if not image_data:
        print()
        print("Could not find image URL.")
        print()
        print("message.images:")
        print(image_list)
        raise RuntimeError("Image URL not found.")
    if image_data.startswith("data:"):
        image_data = image_data.split(
            ",",
            1
        )[1]
    try:
        raw = base64.b64decode(
            image_data
        )
    except Exception as e:
        print()
        print("Base64 decode error:")
        print(e)
        raise
    try:
        image = Image.open(
            io.BytesIO(raw)
        ).convert("RGB")
    except Exception as e:
        print()
        print("Could not open generated image:")
        print(e)
        raise
    return image

print("FAR LANDS GENERATOR")
print()
print(f"Segments: {SEGMENTS}")
print(
    f"Overlap: {int(OVERLAP_PERCENT * 100)}%"
)
print(f"Model: {MODEL}")
print()

generated_images = []
previous_image = None

for i in range(SEGMENTS):

    print()
    print("=" * 60)
    print(
        f"[{i + 1}/{SEGMENTS}] GENERATING"
    )
    print("=" * 60)
    if previous_image is None:
        prompt = PROMPT + """

This is the FIRST segment.

Create the beginning of an enormous vertical
journey through the Minecraft Far Lands.

The bottom edge must contain terrain that can
naturally continue downward.

Do not finish the landscape at the bottom.

The world continues beyond the bottom edge.
"""
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    else:
        overlap_image = get_bottom_overlap(
            previous_image
        )
        print(
            f"Using bottom "
            f"{int(OVERLAP_PERCENT * 100)}% "
            f"as visual overlap."
        )
        overlap_filename = (
            f"far_lands_overlap_{i:02d}.jpg"
        )
        overlap_image.save(
            overlap_filename,
            quality=90
        )
        print(
            f"Overlap saved: "
            f"{overlap_filename}"
        )
        overlap_data_url = image_to_data_url(
            overlap_image
        )
        prompt = PROMPT + f"""

This is segment {i + 1} of a continuous vertical journey
through the Minecraft Far Lands.

The attached reference image shows ONLY the terrain at the
TOP EDGE of the new segment.

IMPORTANT:
The reference is NOT the image to recreate.

You must GENERATE NEW TERRAIN that continues BEYOND the
bottom edge of the reference.

Think of the reference as the last few meters of terrain
that the camera has just passed.

The generated image represents what the camera sees NEXT,
farther down into the world.

DO NOT:
- copy the reference image
- recreate the same mountains
- repeat the same formations
- mirror the reference
- zoom into the reference
- make a near-identical image
- treat the reference as the composition

DO:
- continue the terrain beyond the reference
- extend cliffs into new formations
- introduce new terrain further down
- create new Far Lands distortions
- preserve the same world, atmosphere and visual style
- keep geological continuity at the boundary
- gradually develop completely new terrain below

The TOP of the generated image should connect naturally
to the terrain shown in the reference.

The rest of the generated image must be NEW TERRAIN.

The journey moves vertically from TOP to BOTTOM.

The image must remain upright and portrait-oriented.

Do not rotate the landscape.
Do not create a sideways panorama.
Do not rotate the camera.

Imagine the camera is moving continuously DOWNWARD
through an enormous Far Lands world.

The reference is where the camera was.
The generated image is where the camera goes NEXT.

Create a substantially different landscape below the
boundary while maintaining continuity.

No UI.
No text.
No characters.
"""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": overlap_data_url
                        }
                    }
                ]
            }
        ]
    try:
        response = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "modalities": [
                    "image",
                    "text"
                ],
                "image_config": {
                    "aspect_ratio": "1:8"
                }
            },
            timeout=300
        )
    except requests.RequestException as e:
        print()
        print("REQUEST ERROR:")
        print(e)
        raise
    if not response.ok:
        print()
        print("=" * 60)
        print("API ERROR")
        print("=" * 60)
        print(
            "STATUS:",
            response.status_code
        )
        print()
        print(response.text)
        raise RuntimeError(
            "Hack Club API request failed."
        )
    try:
        data = response.json()
    except Exception:
        print()
        print("Invalid JSON response:")
        print(response.text)
        raise
    image = extract_image(
        data
    )
    print()
    print(
        f"Generated: "
        f"{image.width} x {image.height}"
    )
    filename = (
        f"far_lands_segment_{i + 1:02d}.png"
    )
    image.save(
        filename
    )
    print(
        f"Saved: {filename}"
    )
    generated_images.append(
        image
    )

    previous_image = image

print()
print("=" * 60)
print("STITCHING FINAL IMAGE")
print("=" * 60)

if not generated_images:

    raise RuntimeError(
        "No images were generated."
    )

width = max(
    image.width
    for image in generated_images
)

cropped_images = [
    generated_images[0]
]


for image in generated_images[1:]:

    crop_height = int(
        image.height * OVERLAP_PERCENT
    )

    crop_height = max(
        crop_height,
        1
    )

    cropped = image.crop(
        (
            0,
            crop_height,
            image.width,
            image.height
        )
    )

    cropped_images.append(
        cropped
    )

height = sum(
    image.height
    for image in cropped_images
)


print()
print(
    f"Final size: "
    f"{width} x {height}"
)

result = Image.new(
    "RGB",
    (
        width,
        height
    )
)

y = 0
for i, image in enumerate(cropped_images):
    result.paste(
        image,
        (
            0,
            y
        )
    )
    print(
        f"Placed segment "
        f"{i + 1}/{len(cropped_images)} "
        f"at Y={y}"
    )
    y += image.height
output_file = ("far_lands_tower.png")

result.save(output_file)

print()
print("=" * 60)
print("DONE")
print("=" * 60)

print(
    f"Segments generated: "
    f"{len(generated_images)}"
)

print(
    f"Overlap removed from "
    f"segments 2-{len(generated_images)}: "
    f"{int(OVERLAP_PERCENT * 100)}%"
)

print(
    f"Final image: "
    f"{width} x {height}"
)

print(
    f"Saved: {output_file}"
)