import os
import sys
from datetime import datetime

import anyio
import dagger
import requests
from dagger import dag, BuildArg

async def main():
    # Ensure required environment variables are set
    for var in ["CR_PAT", "USERNAME"]:
        if var not in os.environ:
            raise OSError(f"{var} environment variable must be set")

    # Initialize Dagger client
    cfg = dagger.Config(log_output=sys.stderr)
    async with dagger.connection(cfg):
        username = os.environ["USERNAME"]
        password = dag.set_secret("password", os.environ["CR_PAT"])

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        source = dag.host().directory(project_root)

        # Use Python base container to build and test FastAPI app
        python_app = (
            dag.container()
            # .from_("python:3.12-slim")
            .with_mounted_directory("/app", source)
            # .with_workdir("/app")
            # .with_exec(["pip", "install", "--no-cache-dir", "-r", "requirements.txt"])
        )

        # Build the Docker image using Dagger and Dockerfile
        repo_url = "https://github.com/Javier-Godon/kafka-video-consumer-mongodb-python"
        git_repo = dag.git(repo_url)
        branch = git_repo.branch("main")
        latest_commit = await branch.commit()  # Get the latest commit SHA

        print(f"Latest commit SHA: {latest_commit}")

        # Build Docker image
        build_image = (
            python_app.directory("/app")
            .docker_build(
                dockerfile="./Dockerfile",
                build_args=[BuildArg("tag", latest_commit)], # Pass latest commit SHA as tag
            )
        )

        # Publish image to GHCR
        short_sha = latest_commit[:7]  # Shorten commit hash for tagging
        timestamp = datetime.now().strftime("%Y%m%dT%H%M")
        image_tag = f"{short_sha}-{timestamp}"
        image_address = f"ghcr.io/{username.lower()}/kafka-video-consumer-mongodb-python:{image_tag}"

        address = await build_image.with_registry_auth(
            "ghcr.io", username, password
        ).publish(image_address)

        print(f"Image published at: {address}")

        # Trigger GitHub Action via repository_dispatch
        dispatch_url = "https://api.github.com/repos/Javier-Godon/cluster-continuous-delivery/dispatches"
        headers = {
            "Authorization": f"token {os.environ['CR_PAT']}",
            "Accept": "application/vnd.github+json"
        }

        payload = {
            "event_type": "image-tag-in-kafka-video-consumer-mongodb-python-dev-updated",
            "client_payload": {
                "image_tag": image_tag
            }
        }

        response = requests.post(dispatch_url, json=payload, headers=headers)
        if response.status_code == 204:
            print("GitHub Action triggered successfully")
        else:
            print(f"Failed to trigger GitHub Action: {response.status_code} {response.text}")

anyio.run(main)
