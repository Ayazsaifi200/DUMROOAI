# 🚀 Quick Deploy Instructions

## Streamlit Cloud (Recommended - Free)

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with GitHub
3. **New app** → Select repository: `Ayazsaifi200/DUMROOAI`
4. **Advanced settings** → Add secrets:
   ```
   OPENAI_API_KEY = "your_api_key_here"
   SECRET_KEY = "your_secret_key_here"
   ```
5. **Deploy!**

## Heroku Deploy

```bash
# Install Heroku CLI, then:
heroku login
heroku create dumroo-ai-app
heroku config:set OPENAI_API_KEY="your_key_here"
heroku config:set SECRET_KEY="your_secret_key_here"
git push heroku main
```

## Railway Deploy

1. **Connect**: https://railway.app/
2. **Import** from GitHub: `Ayazsaifi200/DUMROOAI`
3. **Add Variables**:
   - `OPENAI_API_KEY`
   - `SECRET_KEY`
4. **Deploy automatically**

## Local Setup for Others

```bash
git clone https://github.com/Ayazsaifi200/DUMROOAI.git
cd DUMROOAI
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python generate_data.py
streamlit run app.py
```

## Demo Accounts
- `super_admin` / `admin123`
- `north_admin` / `north123`
- `grade89_admin` / `grade123`

## Features
- 🤖 Natural Language Querying (Hindi + English)
- 🔒 Role-Based Access Control
- 📊 Interactive Dashboard
- 💬 AI-powered Conversations
- 📱 Responsive Design