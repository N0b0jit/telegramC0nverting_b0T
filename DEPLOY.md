# Hosting your Bot for FREE (No Trial, No Card) 🚀

If Koyeb is asking for a trial, use **Render.com**. It is 100% free and does not require a credit card.

## 1. Prepare your GitHub
Make sure all your code is pushed to your GitHub repository:
`https://github.com/N0b0jit/telegramC0nverting_b0T.git`

## 2. Sign up on Render.com
1. Go to [Render.com](https://render.com/) and create a free account.
2. You don't need a credit card.

## 3. Create a New Service
1. Click **"New +"** and select **"Web Service"**.
2. Connect your GitHub and select your repository.
3. **Instance Type**: Select **"Free"** ($0/month).
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python bot.py`

## 4. Set Environment Variables
1. Go to the **"Environment"** tab.
2. Click **"Add Environment Variable"**.
3. Key: `TELEGRAM_BOT_TOKEN`
4. Value: `YOUR_BOT_TOKEN`

## 5. CRITICAL: Keep it Awake (24/7)
Render's free tier "sleeps" if nobody visits the web address. To keep your bot running forever:
1. Go to [Cron-job.org](https://cron-job.org/).
2. Create a free account.
3. Create a new **Cronjob**.
4. **URL**: Enter the URL Render gives you (e.g., `https://your-bot.onrender.com`).
5. **Execution**: Set it to run every **14 minutes**.

This will "ping" your bot and keep it 100% online without it ever stopping.

---

### Alternative: Serv00.com (Advanced)
If you want a real Linux server for free:
1. Register at [Serv00.com](https://www.serv00.com/).
2. You get SSH access and Python support forever for free.
