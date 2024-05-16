import tweepy
import cv2
import os
import tempfile

# Enter API tokens below
bearer_token = ''
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# V1 Twitter API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# V2 Twitter API Authentication
client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

# List image directory
image_dir = [# image path 1, image path 2
    ]
max_file_size = 4.5 * 1024 * 1024  # 4.5MB

# Read text from the file
file_path = "post text.txt"
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        print("Successfully read text from the file:")
        print(text)
except Exception as e:
    print("Error occurred:", e)

def resize_image(image_dir, max_file_size):
    img = cv2.imread(image_dir)
    if img is None:
        print(f"Error: Unable to read image at '{image_dir}'")
        return None

    # Calculate current file size
    file_size = os.path.getsize(image_dir)
    print(f"Original file size: {file_size} bytes")

    # Calculate target size (5MB)
    target_file_size = max_file_size

    # Calculate scaling factor to achieve target size
    scaling_factor = (target_file_size / file_size) ** 0.5

    # Resize image
    new_width = int(img.shape[1] * scaling_factor)
    new_height = int(img.shape[0] * scaling_factor)
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Encode the resized image to JPEG format with compression quality
    _, encoded_img = cv2.imencode(".jpg", resized_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    resized_file_bytes = encoded_img.tobytes()
    print(f"Resized file size: {len(resized_file_bytes)} bytes")

    return resized_file_bytes

# List to store media IDs
media_ids = []

# Upload media files and append media IDs to the list
for image_path in image_dir:
    # Resize image
    resized_file_bytes = resize_image(image_path, max_file_size)
    if resized_file_bytes is not None:
        # Save resized image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(resized_file_bytes)
            temp_file_path = temp_file.name
            print(f"Resized image saved to temporary file: {temp_file_path}")

        # Upload resized image to Twitter
        try:
            media = api.media_upload(filename=temp_file_path)
            media_ids.append(media.media_id)
            print(f"Image '{image_path}' uploaded to Twitter")
        except Exception as e:
            print(f"Error occurred while uploading image '{image_path}':", e)

        # Remove temporary file
        os.unlink(temp_file_path)

# Now media_ids contains a list of media IDs
print(media_ids)

# Use media IDs to create a tweet with media attachments
tweet = client.create_tweet(
    text=text,
    media_ids=media_ids
)
print("Tweeted!!")