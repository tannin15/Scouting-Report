import requests


def download_headshot(url, save_path="temp_headshot.png"):
    
    # Downloads a player's MLB headshot.
    # Returns the filename so it can be inserted into Excel.
    
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(
            f"Unable to download headshot ({response.status_code})"
        )

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path