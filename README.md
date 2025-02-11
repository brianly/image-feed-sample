# Image feed sample

## Overview
This project demonstrates how to call the Viva Engage (Yammer) API with an Entra token, iterate over messages in a community, and output only those messages with image attachments. It will also download and save copies of the attached images in the current directory. It is written with [MSAL](https://learn.microsoft.com/en-us/entra/identity-platform/msal-overview) which means it is relatively easy to translate to languages other than Python.

Python 3.13.1 on Windows was used for the creation of this script, but it'll run on macOS and Linux just as well. [Requests](https://pypi.org/project/requests/) and [MSAL](https://pypi.org/project/msal/) are required for making API requests. Using [uv](https://docs.astral.sh/uv/) is recommended for easy setup and execution, but ```pip``` works too.

### Project updates
- 2025-02-03: Improvements including specifying directory for image downloads.
- 2025-01-23: First release demonstrating API usage.


## Getting started

Get familiar with Entra authentication and tokens by reviewing the [Yammer API with AAD tokens Postman Collection](https://techcommunity.microsoft.com/blog/viva_engage_blog/yammer-api-with-aad-tokens-postman-collection/857923) blog post and testing in Postman. Any HTTP client will work, but you'll have extract the endpoints from the downloadable collection on the blog. 

Once you have the API working in Postman with the Entra application you registered then you are ready to use these scripts. If API calls are failing in Postman, fix those before moving on because it will simplify debugging.

## Getting Entra tokens with MSAL
### `acquire_msal_token.py`
This script demonstrates the process required to get an Entra token. It's important to use Entra tokens in this project because legacy Yammer tokens do not work with the file preview or download endpoints illustrated in the code.

Store the token from the output of this script securely. Review Entra guidance and your own internal policies to ensure you are handling tokens securely.

Before running this script, you must [register an Application in Entra](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) and update these constants:

- ```CLIENT_ID```: Take this verbatim from the Entra portal after creating an application.
- ```AUTHORITY```: Replace the tenant ID on the end of the URL.

#### Usage
```powershell
uv run .\src\acquire_msal_token.py
```

#### Example
```powershell
uv run .\src\acquire_msal_token.py
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code [CODE APPEARS HERE] to authenticate.
Access token acquired:
eyJ0eXAiOiJKV1... [TOKEN OUTPUT REMOVED]
```

You can pipe the output directly to a file that you can reference in the ```image_feed.py``` script below.

## Getting messages and images from a community feed
### `image_feed.py`

Fetches only thead starters from the feed and iterates over them. An excerpt for each message with image file attachments will be output. The attached images are saved to the current directory. If you need to output reply or comment messages associated with a thread starter then you need to pass threaded=false to the ```engage_get_request()``` method.

This requires a valid Entra token for Viva Engage. If you use a legacy Viva Engage token then you'll only be able to get output from the messages API and subsequent calls for attachments will fail.

Calls are made to the ```messages/in_group/GROUP_ID.json``` endpoint, but the code can be easily modified to use other message endpoints as the output format is the same.

#### Usage
```powershell
uv run .\src\image_feed.py 202092797952 .\token.txt .\temp\
```
#### Example
```powershell
uv run .\src\image_feed.py 202092797952 .\token.txt .\temp\
Using these arguments...
Community ID: 202092797952
Token Path: .\token.txt
Image Save Path: .\temp\
Excerpt: unique image
Content type: image/png
large_preview_url: https://www.yammer.com/api/v1/uploaded_files/2315560452096/version/2339394756608/large_preview/
Image saved to temp\2315560452096-image.png.png.
download_url: https://www.yammer.com/api/v1/uploaded_files/2315560452096/download
Image saved to temp\downloaded_url-2315560452096-image.png.png.
```

#### Tips

- Get a community ID by navigating to an Engage community on the web, copying the URL, and decoding it with a base64 decoder.
- Use the [pprint](https://docs.python.org/3/library/pprint.html) module to quickly output data structures if you can't debug in an IDE.
- You may need to create a [custom launch.json file](https://code.visualstudio.com/Docs/editor/debugging#_launch-configurations) for debugging in VS Code. Example:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": ["202092797952", "${workspaceFolder}/token.txt"],
        },

    ]
}
```
- In production scenarios, run the script using tokens associated with a normal user account without admin privileges.

## Troubleshooting

### Failed to retrieve data: 401 (Expired signature for Tokie JWT)
This error indicates that your token has expired. Getting a new token with ```acquire_msal_token.py``` should resolve this issue.

### Problems with accessing Viva Engage files
Test with an HTTP client like Postman or Fiddler. Modify the following HTTP request to include your file and a valid Entra token:
```
GET https://www.yammer.com/api/v1/uploaded_files/[REPLACE WITH FILE ID]/version/[REPLACE WITH FILE VERSION ID]/large_preview/ HTTP/1.1
accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
accept-language: "en-US,en;q=0.9"
cache-control: "no-cache"
pragma: "no-cache"
priority: "u=0, i"
sec-ch-ua: "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
sec-ch-ua-mobile: "?0"
sec-ch-ua-platform: "\"Windows\""
sec-fetch-dest: "document"
sec-fetch-mode: "navigate"
sec-fetch-site: "none"
sec-fetch-user: "?1"
upgrade-insecure-requests: "1"

Authorization: "Bearer [REPLACE WITH ENTRA TOKEN]"
```

### Failed to retrieve data: 401 (Fail to find Yammer Oauth token)

Indicates that the token is invalid. Check that the file with the token contains a valid token and is readable by the script. While this error references a Yammer OAuth token you must use an Entra token with the Yammer permission to access the APIs required by this script.

### Failed to retrieve data: 404

This is likely caused by the use of a community ID which is inaccessible to the user. Double-check the community ID is valid by visiting the community via the web with the user that is associated with the token.

### Failed to save image: [Errno 2] No such file or directory: 'tempsdfds\\2315560452096-image.png.png'

Errors like this result from an invalid ```image_save_path``` path passed to the script. Make sure the directory exists and is writable.

## License
This project is licensed under the MIT License.

## Help and support
For general issues or questions, please file an issue in this repo.

There is no formal support for this script and some issues may not be resolved. Please do not send requests to Microsoft Support asking for help with code in this repo as it is intended for demonstration purposes only.


