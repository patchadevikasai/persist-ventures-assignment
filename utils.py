import requests
import os

# Replace these with your Instagram Access Token and Flic Token
access_token = "IGQWRPWllrRkNTR3k5SHhXdkpuSFZABVkRjLWQxTXVtcG9LY2RHdVJMQlkzQXRHN2lmZAFJCb2FmRExSM05pX2ptUm1BbGxnTldlLUh3UEJUMWMtdHlWWkdWUzNBR3I1NWtoY0JQMm9Way1kTVpxWDQxV1AtYTB2d28ZD"
flic_token = "flic_da5a13caa14f0cc5c124532ef942f8c9986907e3ed6fe4778cdd1ecf74aec22c"
category_id = 25  # Category ID for Empowerse

# Instagram user ID and media URL
url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"

# Function to fetch Instagram profile data
def get_profile_data():
    response = requests.get(url)
    profile_data = response.json()
    if 'id' in profile_data:
        print(f"Profile Data: {profile_data}")
        return profile_data
    else:
        print("Failed to fetch profile data.")
        return None

# Fetch media posts of the authenticated user
def get_media(user_id):
    media_url = f"https://graph.instagram.com/{user_id}/media?fields=id,caption,media_type,media_url&access_token={access_token}"
    response = requests.get(media_url)
    media_data = response.json()

    if 'data' in media_data:
        print(f"Fetched {len(media_data['data'])} media posts.")
        return media_data['data']
    else:
        print("Failed to fetch media.")
        return None

# Filter posts by hashtag in the caption
def filter_posts_by_hashtag(posts, hashtag):
    filtered_posts = []
    for post in posts:
        if post.get('caption') and hashtag.lower() in post['caption'].lower():
            filtered_posts.append(post)
    return filtered_posts

# Get the upload URL from Empowerse
def get_upload_url():
    url = "https://api.socialverseapp.com/posts/generate-upload-url"
    headers = {
        "Flic-Token": f"{flic_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            response_data = response.json()
            upload_url = response_data.get('url')
            if upload_url:
                print(f"Upload URL: {upload_url}")
                return upload_url
            else:
                print("No upload URL found in the response.")
                return None
        except ValueError:
            print("Failed to parse response as JSON.")
            return None
    else:
        print(f"Failed to get upload URL. HTTP Status Code: {response.status_code}")
        return None

# Upload media to Empowerse
def upload_media(upload_url, media_filename):
    try:
        with open(media_filename, 'rb') as media_file:
            response = requests.put(upload_url, files={'file': media_file})

            if response.status_code == 200:
                print("Upload successful.")
                etag = response.headers.get('ETag')
                if etag:
                    print(f"Upload successful. ETag: {etag}")
                    return {"etag": etag}
                else:
                    print("No ETag found in the response headers.")
                    return None
            else:
                print(f"Failed to upload media. Status code: {response.status_code}")
                return None
    except requests.exceptions.RequestException as e:
        print(f"Error during upload: {e}")
        return None

# Create a post in Empowerse feed
# Create a post in Empowerse feed
def create_post(etag, title):
    if not etag:
        print("Error: ETag is missing.")
        return

    url = "https://api.socialverseapp.com/posts"
    headers = {
        "Flic-Token": f"{flic_token}",
        "Content-Type": "application/json"
    }
    
    # Make sure etag is passed correctly as the hash
    body = {
        "title": title,
        "hash": etag.strip('"'),  # Strip any extra quotes from etag
        "is_available_in_public_feed": False,  # Set to True if you want public visibility
        "category_id": category_id
    }

    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        print(f"Post created successfully with title: {title}")
    else:
        print(f"Failed to create post. Status Code: {response.status_code}")
        print("Response content:", response.text)

# Function to delete video file from the folder after uploading
def delete_video_file(media_filename):
    try:
        os.remove(media_filename)
        print(f"File {media_filename} deleted from folder.")
    except Exception as e:
        print(f"Error deleting file {media_filename}: {e}")

# Main execution
if __name__ == "__main__":
    # Step 1: Ensure the 'video' folder exists
    video_folder = "video"
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)

    # Step 2: Get profile data
    profile_data = get_profile_data()

    if profile_data:
        user_id = profile_data["id"]

        # Step 3: Fetch media from the user
        user_media = get_media(user_id)
        if user_media:
            for post in user_media:
                print(f"Post ID: {post['id']} - Caption: {post.get('caption', 'No caption')}")

            # Step 4: Filter posts that contain the 'motivational' hashtag
            filtered_posts = filter_posts_by_hashtag(user_media, "motivational")
            if filtered_posts:
                print(f"Found {len(filtered_posts)} posts with the 'motivational' hashtag: ")
                for post in filtered_posts:
                    print(f"Post ID: {post['id']} - Caption: {post.get('caption', 'No caption')}")

                # Step 5: Get the upload URL
                upload_url = get_upload_url()

                # Step 6: Download and upload media to Empowerse
                if upload_url:
                    for post in filtered_posts:
                        media_url = post.get('media_url')
                        if media_url:
                            media_type = post.get('media_type')
                            # Determine file extension based on media type
                            if media_type == 'IMAGE':
                                file_extension = '.jpg'  # or .png based on the type
                            elif media_type == 'VIDEO':
                                file_extension = '.mp4'
                            else:
                                print(f"Unsupported media type: {media_type}")
                                continue

                            # Set the download path to the 'video' folder
                            media_filename = f"{video_folder}/{post['id']}{file_extension}"

                            # Download the media and save it locally in the 'video' folder
                            img_data = requests.get(media_url).content
                            with open(media_filename, 'wb') as f:
                                f.write(img_data)
                            print(f"Downloaded media {media_filename}")
                            
                            # Upload the media
                            upload_response = upload_media(upload_url, media_filename)
                            if upload_response:
                                etag = upload_response.get("etag")  # Use ETag here
                                # Step 7: Create a post in Empowerse
                                create_post(etag, post.get('caption', 'No Title'))

                                # Step 8: Delete the video file after upload
                                delete_video_file(media_filename)
                            else:
                                print("Failed to get ETag from upload response.")
