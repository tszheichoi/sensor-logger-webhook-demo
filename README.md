# Sensor Logger Webhook Demo

This project is a FastAPI demo for handling webhook notifications from Sensor Logger. When a user uploads a new recording to a Study, Sensor Logger sends a POST request to the `/` endpoint. The server downloads the recording, extracts it, runs a dummy analysis, and posts a markdown summary back to Sensor Logger.

## API Endpoints

The FastAPI app implements a POST endpoint that conforms to the documentation at https://github.com/tszheichoi/awesome-sensor-logger/blob/main/STUDY_WEBHOOKS.md. It receives JSON payload with `studyId`, `uploadId`, and `secretCode`, and processes the uploaded data in the background. It also posts a dummy markdown report back to Sensor Logger, which can be viewed in-app.

## Running the Server

### Locally

This is the simplest setup, useful for testing and experimentation.

1. Install dependencies with pip:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```

The server is exposed under `http://localhost:8000/docs`. However, this URL is not accessible from the internet, so Sensor Logger Cloud cannot deliver webhook requests to it. To test webhooks during development, you must expose your local machine using a tunnelling service such as ngrok.

Create an ngrok account at https://ngrok.com/. After logging in, you will see an Auth Token in your dashboard — copy it for later. If you are on a Mac, you can install via `brew install ngrok`. On other platforms, you may download the installer from your ngrok dashboard. Once installed, you need to add your Auth Token using `ngrok config add-authtoken <YOUR_TOKEN_HERE>`. This links your machine to your ngrok account and enables stable tunnels.

Now, create a public tunnel with command `ngrok http 8000`. ngrok will print something like:

```
Forwarding    https://xxxx-86-12-99-41.ngrok-free.app -> http://localhost:8000
```

The important part is the public HTTPS URL (not the localhost one!), which you will use when configuring the Study. In this example, the webhook endpoint required in Sensor Logger is `https://xxxx-86-12-99-41.ngrok-free.app`.

### Cloud Deployment

For production use, deploy the FastAPI app to a cloud provider such as AWS, GCP, or Azure. Ensure that the server is accessible over HTTPS. A simple and free option is to use Railway:

1. Create a free account on https://railway.app/.
2. Create a new project and link it to a forked copy of this repository on your github.
3. Deploy the project. Railway will automatically install dependencies and start the server.
4. Once deployed, you need to "expose" the service to get a public URL. Click on the project, then settings then in the networking section "Generate Domain". Once generated, copy the URL and use it when configuring the Study.

## Customization

- Replace the dummy algorithm in `run_algorithm()` with your own analysis logic.
- Adjust endpoint or processing as needed for your use case.
- Adjust the analysis depending on the export format used. The demo assumes a zip file containing raw sensor data.
