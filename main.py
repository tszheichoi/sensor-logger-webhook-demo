import logging
import shutil
import traceback
import zipfile
import uvicorn
import httpx
from datetime import datetime
from pathlib import Path
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_URL = "https://sensorlogger.app/api"

class WebhookRequest(BaseModel):
    studyId: str
    uploadId: str
    secretCode: str

app = FastAPI(title="Webhook Demo for Sensor Logger Studies")
tmp_dir = Path(__file__).parent / "tmp"
tmp_dir.mkdir(exist_ok=True)

@app.post("/")
async def process_webhook(request: WebhookRequest, background_tasks: BackgroundTasks):
    """
    Webhook endpoint that receives file upload notifications from Sensor Logger
    when a user uploads a new recording.
    """
    background_tasks.add_task(
        process_recording,
        request.studyId,
        request.uploadId,
        request.secretCode,
    )
    return {"status": "processing"}

async def process_recording(
    study_id: str, upload_id: str, secret_code: str
):
    """
    Process a recording by:
    1. Download the recording using the provided study ID, upload ID, and secret code.
    2. Extract the zip file. (Assuming the export format for the Study is set to Zip CSV.)
    3. Run algorithm by calling `run_algorithm`.
    4. Post results back to the Sensor Logger API.
    """
    upload_dir = tmp_dir / upload_id
    try:
        download_url = f"{BASE_URL}/study/file/v1?studyId={study_id}&uploadId={upload_id}"
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(
                download_url, headers={"Authorization": secret_code}
            )
            response.raise_for_status()

            upload_dir.mkdir(exist_ok=True)
            zip_path = upload_dir / "recording.zip"
            zip_path.write_bytes(response.content)
            logger.info(f"Saved zip file: {zip_path}, size: {zip_path.stat().st_size} bytes")

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(upload_dir)

            logger.info(f"Extracted zip file to: {upload_dir}")

            markdown_output = await run_algorithm(upload_dir)

            upload_url = f"{BASE_URL}/study/webhook/v1?studyId={study_id}&uploadId={upload_id}"
            upload_response = await client.put(
                upload_url,
                headers={
                    "Authorization": secret_code,
                    "Content-Type": "text/markdown"
                },
                content=markdown_output,
            )
            upload_response.raise_for_status()
    except Exception as e:
        logger.error(f"Error processing {upload_id}: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
            logger.info(f"Cleaned up upload directory: {upload_dir}")

async def run_algorithm(data_path: Path) -> str:
    """
    Dummy algorithm: returns a markdown report with example Sensor Logger data summary.
    Args:
        data_path (Path): Path to the extracted sensor data directory.
    Returns:
        str: Markdown report summarizing the data.
    """
    markdown = "# Sensor Logger Data Summary\n"
    markdown += f"Generated on {datetime.utcnow().isoformat()} UTC\n\n"
    markdown += f"Extracted number of files: {len(list(data_path.glob('**/*')))}\n\n"
    markdown += "## Example Analysis\n\n"
    markdown += "Lorem ipsum dolor sit amet consectetur adipiscing elit.\n\n"
    markdown += "*This is a dummy report generated for demonstration purposes.*\n"
    return markdown

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
