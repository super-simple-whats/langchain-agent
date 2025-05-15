# SuperSimpleWhats API - WhatsApp AI Agent

This project implements a conversational AI agent for WhatsApp using the SuperSimpleWhats API and LangChain/LangGraph with Anthropic's language models.

## Features

- Real-time AI-powered conversations via WhatsApp
- Example agent tools (like web search and whatsapp message sender)
- Streaming responses for natural conversation flow
- Conversation state management with reset capabilities
- Webhook integration for processing WhatsApp messages

## Prerequisites

- Python 3.9+ 
- A [SuperSimpleWhats](https://supersimplewhats.com/) account, with a registered device and API key
- A WhatsApp account already running in a device
- A [NGROK](https://ngrok.com/) account (for webhook testing)
- An Anthropic API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/super-simple-whats/langchain-agent.git
    cd langchain-agent
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your device in SuperSimpleWhats (if you haven't already). In this example, we are using jq for the response parsing and qrencode for the qrcode generation. Make sure you have them installed:
    ```bash
    curl --location 'https://app.supersimplewhats.com/v1/devices/register_device' \
    --header 'Content-Type: application/json' --header 'Authorization: <your-ssw-api-key>' \
    --data '{"name":"<your-device-name>"}' | jq -r '.data' | qrencode -t ANSIUTF8
    ```
    After generating the QR code, scan it with your WhatsApp app to link the device. This will allow you to send and receive messages through the SuperSimpleWhats API.
    If you need extra help with the device setup, please refer to the [SuperSimpleWhats documentation](https://documenter.getpostman.com/view/11336124/2sB2j7eVjW#ccdeedc5-ed46-429f-8ec6-cc19ecbbe310).

5. Create a `.env` file in the root directory and add your API keys:
    ```bash
    MODEL_NAME=claude-3-5-sonnet-20240620
    ANTHROPIC_API_KEY=<your_anthropic_api_key>
    TAVILY_API_KEY=<your_tavily_api_key>
    HOOKS_PATH=/hooks
    HOOKS_PORT=8080
    DEVICE_NAME=<your_device_name>
    SSW_API_KEY=<your_ssw_api_key>
    ```

6. Install the `ngrok` to expose your local server to the internet.
    ##### For Mac
    ```bash
    brew install ngrok
    ```
    ##### For Linux
    ```bash
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
      | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
      && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
      | sudo tee /etc/apt/sources.list.d/ngrok.list \
      && sudo apt update \
      && sudo apt install ngrok
    ```
    ##### For Windows
    If you are using Windows, you can download the installer from the [ngrok website](https://ngrok.com/download).

7. Start ngrok to expose your local server, for example:
    ```bash
    ngrok http 8080
    ```

8. Set your ngrok URL as webhook URL in your SuperSimpleWhats account. The URL should look like this:
    ```bash
    curl -X POST --header \
    "Authorization: <your-ssw-api-key>" \
    --data '{"device_name":"<your-device-name>", "url":"https://<your-ngrok-subdomain>.ngrok.io/hooks"}' \
    https://app.supersimplewhats.com/v1/devices/hook_endpoints/add 
    ```

9. Run the application:
    ```bash
    python start_whatsapp.py
    ```

## Usage

- Send messages to your registered device to interact with the AI agent.
- You can use tools like "search the web for x" or "send a whatsapp message to x" to perform actions.
- Send "/reset" or "reset" to clear the conversation history and start fresh

## How it works

1. WhatsApp messages are received through the SuperSimpleWhats API webhook
2. Messages are processed by the LangGraph-powered conversation graph
3. The AI generates responses which are streamed back to the user via SSW API
4. Conversation state is maintained for each unique chat until /reset is sent
5. The application can be extended with additional tools and features as needed

## Note

This is a demonstration project and may require additional configuration and error handling for production use.