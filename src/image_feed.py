import argparse
from pathlib import Path

import requests


def read_text(file_path) -> str:
    """
    Reads the content of a text file and returns it as a string.

    Args:
        file_path (str): The path to the text file to be read.

    Returns:
        str: The content of the file as a string, or None if an error occurs.

    Prints:
        Prints the file path being read.
        Prints an error message if the file is not found, permission is denied,
        the file is not in a valid Unicode format, or any other exception occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("The file was not found. Please check the file path.")
    except PermissionError:
        print(
            "Permission denied. You do not have the necessary permissions to read the file."
        )
    except UnicodeDecodeError:
        print("The file is not in a valid Unicode format.")

    return None


def engage_get_request(path, token, query_params=None):
    """
    Make a GET request to a Viva Engage endpoint.

    Args:
        path (str): The API endpoint path.
        token (str): The authorization token.
        params (dict, optional): Additional parameters for the request. Defaults to None.

    Returns:
        tuple: A tuple containing the request headers and the response object.
    """
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(
        f"https://www.yammer.com/api/v1/{path}",
        headers=headers,
        timeout=180,
        params=query_params,
    )

    return headers, response


def engage_file_download(url, token):
    """
    Downloads a file from Viva Engage using a direct URL with support for redirects.

    Args:
        url (str): The direct download URL of the file.
        token (str): The authorization token.

    Returns:
        bytes: The content of the file as bytes, or None if an error occurs.
    """
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url, headers=headers, timeout=180)

    if response.status_code == 200:
        return response.content
    elif response.status_code == 302:
        redirect_url = response.headers.get("Location")
        if redirect_url:
            response = requests.get(redirect_url, headers=headers, timeout=180)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download file after redirect: {response.status_code}")
        else:
            print("Redirect location not provided.")
    else:
        print(f"Failed to download file: {response.status_code} ({response.text})")

    return None


def save_image_to_disk(image_data, file_name, save_path):
    """
    Saves binary image data to disk.

    Args:
        image_data (bytes): The binary data of the image.
        file_path (str): The path where the image will be saved.
    """
    try:
        path = Path(save_path) / file_name
        with open(path, "wb") as file:
            file.write(image_data)
        print(f"Image saved to {path}.")
    except Exception as e:
        print(f"Failed to save image: {e}")


def main(params) -> int:
    if params.community_id is not None:
        token = read_text(params.token_path)

        query_params = {
            "threaded": "true",  # Only thread starters when true
            "limit": "10",  # Limit messages per request
        }

        headers, response = engage_get_request(
            f"messages/in_group/{params.community_id}.json", token, query_params
        )

        if response.status_code == 200:
            data = response.json()

            # Find and iterate over the messages element in the JSON from any messages endpoint.
            if "messages" in data:
                messages = data["messages"]
                for message in messages:

                    # Check if the message has attachments
                    if len(message["attachments"]) > 0:

                        # Print an excerpt to understand which message this is.
                        print(f"Excerpt: {message["content_excerpt"]}")

                        # Iterate over the attachments remembering that these may not always be images.
                        for attachment in message["attachments"]:
                            if attachment["type"] == "image":

                                # You may need to switch based on the image type in the response
                                # so you can use different output code.
                                print(f"Content type: {attachment["content_type"]}")

                                # Option 1: Use the large preview. May not be high enough resolution.
                                print(
                                    f"large_preview_url: {attachment["large_preview_url"]}"
                                )

                                large_preview = engage_file_download(
                                    attachment["large_preview_url"], token
                                )

                                image_file_name = (
                                    f'{attachment["id"]}-{attachment["name"]}.png'
                                )

                                save_image_to_disk(
                                    large_preview,
                                    image_file_name,
                                    params.image_save_path,
                                )

                                # Option 2: Get the original file. Higher resolution.
                                print(f"download_url: {attachment["download_url"]}")

                                full_download = engage_file_download(
                                    attachment["download_url"], token
                                )

                                image_file_name = f'downloaded_url-{attachment["id"]}-{attachment["name"]}.png'

                                save_image_to_disk(
                                    full_download,
                                    image_file_name,
                                    params.image_save_path,
                                )

            else:
                print(
                    "No messages found in the response. Check that a messages endpoint was used (e.g., messages/in_group/{group_id}.json)."
                )
        else:
            print(f"Failed to retrieve data: {response.status_code} ({response.text})")
    else:
        print("No community ID provided.")

    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Fetches a feed of messages with images from a Viva Engage community."
    )

    parser.add_argument(
        "community_id",
        type=str,
        help="Community ID in integer format. Use a Base64 decoder to get the ID from a community URL.",
    )

    parser.add_argument(
        "token_path",
        type=str,
        help="Path to an Entra token which has been authorized for the Yammer (Viva Engage) API.",
    )

    parser.add_argument(
        "image_save_path",
        type=str,
        help="Path where downloaded images will be saved.",
    )

    args = parser.parse_args()

    print("Using these arguments...")
    print(f"Community ID: {args.community_id}")
    print(f"Token Path: {args.token_path}")
    print(f"Image Save Path: {args.image_save_path}")

    main(args)
