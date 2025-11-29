# 🔑 How to Get Your Google Gemini API Key

## Quick Steps (2 minutes)

### 1. Go to Google AI Studio
You already have it open! 🎉
- URL: https://aistudio.google.com

### 2. Click "Get API Key"
Look for a button that says:
- "Get API key" or
- "Get started" or
- "Create API key"

### 3. Sign in with Google
Use your Google account to sign in.

### 4. Accept Terms of Service
- Review the Google APIs Terms of Service
- Review the Gemini API Additional Terms of Service
- Check the boxes and click "Continue"

### 5. Create API Key
You'll see options:
- **Create API key in new project** (recommended for first time)
- **Create API key in existing project**

Click "Create API key in new project"

### 6. Copy Your API Key
- Your API key will be displayed
- Click the "Copy" button
- **IMPORTANT**: Save it somewhere safe!

## 🎯 Visual Guide

```
Google AI Studio Homepage
         ↓
   Click "Get API Key"
         ↓
   Sign in with Google
         ↓
   Accept Terms of Service
         ↓
   Create API key in new project
         ↓
   Copy the API key
         ↓
   Paste into .env file
```

## 📝 After Getting the Key

### Add to .env file:
```bash
cd /Users/jaiyankargupta/hrx_hacks/billextraction
echo "GOOGLE_API_KEY=YOUR_ACTUAL_KEY_HERE" > .env
```

Or edit manually:
```bash
nano .env
```

Then paste:
```
GOOGLE_API_KEY=AIzaSy...your_key_here
```

## ✅ Verify It Works

Test your API key:
```bash
# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn app:app --reload

# In another terminal, test
python test_api.py
```

## 🆓 Free Tier Limits

Google Gemini API Free Tier:
- ✅ **1,500 requests per day** (Gemini 1.5 Flash)
- ✅ **15 requests per minute**
- ✅ **1 million tokens per minute**
- ✅ **Perfect for testing and hackathons!**

For Gemini 2.0 Flash:
- ✅ **10 requests per minute** (free tier)
- ✅ **4 million tokens per day**

## 🔒 Security Best Practices

1. **Never commit .env to Git**
   ```bash
   # Already in .gitignore
   .env
   ```

2. **Don't share your API key publicly**

3. **Add API key restrictions** (optional):
   - Go to Google Cloud Console
   - Navigate to APIs & Services → Credentials
   - Click on your API key
   - Add restrictions (IP addresses, HTTP referrers, etc.)

## 🚨 Troubleshooting

### "API key not valid"
- Make sure you copied the entire key
- Check for extra spaces
- Verify the key is for Gemini API

### "Quota exceeded"
- You've hit the free tier limit
- Wait for the quota to reset (daily)
- Or upgrade to paid tier

### "Permission denied"
- Make sure Gemini API is enabled in your project
- Go to Google Cloud Console → APIs & Services → Enable APIs
- Search for "Generative Language API" and enable it

## 📚 Additional Resources

- **Google AI Studio**: https://aistudio.google.com
- **API Documentation**: https://ai.google.dev/docs
- **Pricing**: https://ai.google.dev/pricing
- **Quickstart Guide**: https://ai.google.dev/gemini-api/docs/quickstart

## 🎓 What's Next?

After getting your API key:

1. ✅ Add to `.env` file
2. ✅ Run `./setup.sh` if you haven't
3. ✅ Start the server: `uvicorn app:app --reload`
4. ✅ Test with: `python test_api.py`
5. ✅ Start extracting bills! 🚀

---

**Need help?** The API key should look like: `AIzaSy...` (starts with AIza)
