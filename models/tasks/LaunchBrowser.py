import requests
from bs4 import BeautifulSoup
from models.tasks.Task import Task
from utils.constants import ALLOWED_WEBSITE_URLS
from urllib.parse import urlparse

class LaunchBrowserTask(Task):

    async def execute(self):
        try:
            # Set task status to "RUNNING"
            await self.setStatus("RUNNNING")

            # Get the website URL from inputs
            websiteUrl = self.inputs["websiteUrl"]

            # Check if the website URL is provided
            if websiteUrl is None:
                raise ValueError("No website url provided")
            
            # Ensure the URL starts with http or https
            if not websiteUrl.startswith(("http://", "https://")):
                websiteUrl = f"https://{websiteUrl}"

            # Extract the hostname from the URL
            hostname = urlparse(websiteUrl).netloc

            # Check if the hostname is in the allowed list
            if hostname not in ALLOWED_WEBSITE_URLS:
                raise ValueError(f"Access to {hostname} is not allowed")

            # Fetch the webpage content
            webPageResponse = requests.get(ensure_https(websiteUrl))

            # Check if the request was successful
            if webPageResponse.status_code != 200:
                raise ValueError("Failed")
            
            # Parse the webpage content with BeautifulSoup
            webPage = BeautifulSoup(webPageResponse.content, "html.parser")

            # Set the parsed webpage as an output
            await self.setOutputs({"webPage": webPage})
            
            # Set task status to "COMPLETED"
            await self.setStatus("COMPLETED")
            return self.outputs
        except Exception as e:
            # Set task status to "FAILED" if an exception occurs
            await self.setStatus("FAILED")
            raise ValueError(e)

# Helper function to ensure the URL uses https
def ensure_https(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"https://{url}"
    return url
