# Image feed sample

## Overview
This project demonstrates how to call the Viva Engage (Yammer) API with an Entra token, iterative over messages in a community, and output only those messages with image attachments. It will also download and save copies of the attached images in the current directory. It is written with [MSAL](https://learn.microsoft.com/en-us/entra/identity-platform/msal-overview) which means it is relatively easy to translate to languages other than Python.

Python 3.13.1 on Windows was used for the creation of this script, but it'll run on macOS and Linux just as well. [Requests](https://pypi.org/project/requests/) and [MSAL](https://pypi.org/project/msal/) are required for making API requests. Using [uv](https://docs.astral.sh/uv/) is recommended for easy setup and execution, but ```pip``` should work just fine.

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

## Getting messages and images from a community feed
### `image_feed.py`

Fetches only thead starters from the feed and iterates over them. An excerpt for each message with image file attachments will be output. The attached images are saved to the current directory. If you need to output reply or comment messages associated with a thread starter then you need to pass threaded=false to the ```engage_get_request()``` method.

This requires a valid Entra token for Viva Engage. If you use a legacy Viva Engage token then you'll only be able to get output from the messages API and subsequent calls for attachments will fail.

Calls are made to the ```messages/in_group/GROUP_ID.json``` endpoint, but the code can be easily modified to use other message endpoints as the output format is the same.

#### Usage
```powershell
uv run .\src\image_feed.py 202092797952 token.txt
```
#### Example
```powershell
uv run .\src\image_feed.py 202092797952 token.txt
Using these arguments...
Community ID: 202092797952
Token Path: token2.txt
Entered main()...
token2.txt
Excerpt: unique image
Content type: image/png
large_preview_url: https://www.yammer.com/api/v1/uploaded_files/2315560452096/version/2339394756608/large_preview/
Image saved to 2315560452096-image.png.png.
download_url: https://www.yammer.com/api/v1/uploaded_files/2315560452096/download
Image saved to downloaded_url-2315560452096-image.png.png.
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
## Troubleshooting

### Failed to retrieve data: 401 (Expired signature for Tokie JWT)
This error indicates that your token has expired. Getting a new token with ```acquire_msal_token.py``` should resolve this issue.

## License
This project is licensed under the MIT License.

## Help and support
For general issues or questions, please file an issue in this repo.

There is no formal support for this script and some issues may not be resolved. Please do not send requests to Microsoft Support asking for help with code in this repo as it is intended for demonstration purposes only.


