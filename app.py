"""
Clawdbot - Classic Sports Barbershop Chatbot
Flask backend with local Mistral LLM integration
"""

import os
import json
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv('/home/dee/.openclaw/workspace/local_llm.env')

app = Flask(__name__)

# Configuration
LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://192.168.35.251:8081/v1')
LLM_MODEL = os.getenv('LLM_MODEL', 'mistral')

# Business information
BUSINESS_INFO = {
    'name': 'Classic Sports Barbershop',
    'hours': 'Mon-Sat: 9AM-7PM, Sun: 10AM-4PM',
    'location': '123 Main Street, Downtown',
    'phone': '(555) 123-4567',
    'services': {
        'haircut': '$25',
        'shave': '$20',
        'haircut + shave': '$40',
        'beard trim': '$15',
        'kids haircut': '$20'
    }
}

# Appointment storage (in-memory for POC)
appointments = []

# System prompt for the LLM
SYSTEM_PROMPT = """You are a friendly chatbot for Classic Sports Barbershop. Your job is to:
1. Help customers book appointments
2. Answer questions about services, hours, location, and pricing

Business Information:
- Name: Classic Sports Barbershop
- Hours: Mon-Sat: 9AM-7PM, Sun: 10AM-4PM
- Location: 123 Main Street, Downtown
- Phone: (555) 123-4567
- Services & Pricing:
  - Haircut: $25
  - Shave: $20
  - Haircut + Shave: $40
  - Beard Trim: $15
  - Kids Haircut: $20

When collecting appointment info, ask for:
- Name
- Phone number
- Preferred date and time
- Service wanted

Be concise, friendly, and helpful. If they want to book, summarize the appointment and confirm.
"""

def call_llm(messages):
    """Call the local Mistral model"""
    try:
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Sorry, I'm having trouble connecting to my brain. Please try again. Error: {str(e)}"

def extract_appointment_info(message):
    """Simple extraction of appointment details from user message"""
    info = {}
    message_lower = message.lower()
    
    # Extract name (look for patterns like "my name is X" or just capture words)
    name_match = re.search(r"(?:my name is|i'm|i am)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)", message_lower)
    if name_match:
        info['name'] = name_match.group(1).title()
    
    # Extract phone (simple pattern)
    phone_match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', message)
    if phone_match:
        info['phone'] = phone_match.group(1)
    
    # Extract service
    services = ['haircut', 'shave', 'beard trim', 'kids haircut']
    for service in services:
        if service in message_lower:
            info['service'] = service
            break
    
    # Extract date (simple patterns)
    date_match = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow)', message_lower)
    if date_match:
        info['date'] = date_match.group(1).title()
    
    # Extract time
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', message_lower)
    if time_match:
        hour = time_match.group(1)
        minute = time_match.group(2) or '00'
        period = time_match.group(3) or 'pm'
        info['time'] = f"{hour}:{minute}{period}"
    
    return info

def is_booking_intent(message):
    """Check if message indicates booking intent"""
    booking_keywords = ['book', 'appointment', 'schedule', 'reserve', 'want a haircut', 'need a cut']
    return any(kw in message.lower() for kw in booking_keywords)

def is_hours_query(message):
    """Check if message is about hours"""
    return 'hour' in message.lower() or 'open' in message.lower() or 'close' in message.lower()

def is_services_query(message):
    """Check if message is about services"""
    service_keywords = ['service', 'price', 'cost', 'how much', 'offer', 'do you have']
    return any(kw in message.lower() for kw in service_keywords)

@app.route('/')
def index():
    """Serve the HTML interface"""
    return render_template('index.html', business=BUSINESS_INFO)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Check for specific query types first
    if is_hours_query(user_message):
        response = f"📅 **Hours of Operation**\n\n{BUSINESS_INFO['hours']}\n\nFeel free to stop by or book an appointment!"
    elif is_services_query(user_message):
        services_text = "✂️ **Our Services & Prices**\n\n"
        for service, price in BUSINESS_INFO['services'].items():
            services_text += f"- {service.title()}: {price}\n"
        response = services_text + "\nWould you like to book an appointment?"
    elif 'location' in user_message.lower() or 'address' in user_message.lower():
        response = f"📍 **Find Us**\n\n{BUSINESS_INFO['name']}\n{BUSINESS_INFO['location']}\n\nCall us: {BUSINESS_INFO['phone']}"
    elif 'phone' in user_message.lower() or 'contact' in user_message.lower():
        response = f"📞 **Contact Us**\n\nPhone: {BUSINESS_INFO['phone']}\nLocation: {BUSINESS_INFO['location']}"
    elif is_booking_intent(user_message):
        # Extract any info we already have
        extracted = extract_appointment_info(user_message)
        if extracted:
            # Save partial appointment
            appointments.append(extracted)
            response = "Great! I'd be happy to help you book an appointment.\n\n"
            response += f"I have: {json.dumps(extracted)}\n\n"
            response += "What else should I know? (Any missing info like date/time)"
        else:
            response = """📅 **Book an Appointment**!

To schedule your visit, please provide:
1. Your name
2. Phone number
3. Preferred date
4. Preferred time
5. Service you want (haircut, shave, etc.)

What works for you?"""
    else:
        # Use LLM for general queries
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        response = call_llm(messages)
    
    return jsonify({
        'response': response,
        'extracted_info': extract_appointment_info(user_message)
    })

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments (for POC)"""
    return jsonify({'appointments': appointments})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'llm_url': LLM_BASE_URL})

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
