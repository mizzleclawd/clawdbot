# Clawdbot - Classic Sports Barbershop Chatbot

A simple POC chatbot for Classic Sports Barbershop that takes customer appointments and answers questions about services and hours.

## Features

- 📅 **Appointment Booking** - Collect customer name, phone, preferred date/time, and service
- ℹ️ **Information Queries** - Answer questions about services, hours, pricing, and location
- 🤖 **Local LLM** - Uses Mistral model running locally (no external API costs)
- 🌐 **Simple HTML Interface** - Easy-to-use web frontend for testing

## Quick Start

### 1. Start the Local LLM Server

Ensure Mistral is running at `http://192.168.35.251:8081/v1`

### 2. Install Dependencies

```bash
pip install flask python-dotenv requests
```

### 3. Run the Chatbot

```bash
python app.py
```

### 4. Open the Interface

Navigate to `http://localhost:5000` in your browser

## Project Structure

```
clawdbot/
├── app.py              # Flask backend with chatbot logic
├── local_llm.env       # LLM configuration
├── templates/
│   └── index.html      # HTML frontend
├── static/
│   └── style.css       # Styling
└── DEPLOY.md           # Deployment documentation
```

## Chatbot Capabilities

### Appointment Booking
The bot collects:
- Customer name
- Phone number
- Preferred date and time
- Service type (e.g., haircut, shave, combo)

### Information Queries
The bot can answer:
- What are your hours?
- What services do you offer?
- How much does a haircut cost?
- Where are you located?
- What payment methods do you accept?

## API Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/health` - Health check endpoint

## Customization

### Modify Business Info
Edit `app.py` to update:
- Business hours
- Services and pricing
- Location details
- Appointment scheduling rules

### Prompt Engineering
Modify the `SYSTEM_PROMPT` in `app.py` to customize the bot's personality and knowledge.

## License

POC - For demonstration purposes
