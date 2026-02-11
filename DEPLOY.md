# Deploying your Telegram Bot for FREE 🚀

To host this bot 24/7 without paying any money or using a trial, the best platform right now is **Koyeb**.

## 1. Prepare your GitHub
Make sure all your code (including `requirements.txt`, `Procfile`, and `bot.py`) is pushed to your GitHub repository:
`https://github.com/N0b0jit/telegramC0nverting_b0T.git`

## 2. Sign up on Koyeb
1. Go to [Koyeb.com](https://www.koyeb.com/) and create a free account.
2. You don't need a credit card for the "Nano" instance.

## 3. Create a New Service
1. Click **"Create Service"**.
2. Select **GitHub** as the deployment method.
3. Connect your GitHub account and select your `telegramC0nverting_b0T` repository.

## 4. Configure the Deployment
- **Branch**: `main`
- **Instance Type**: Select **"Nano"** (This is the free one).
- **Service Type**: Select **"Web Service"** (Even though it's a bot).
- **Environment Variables**:
  - Click **"Add Variable"**.
  - Name: `TELEGRAM_BOT_TOKEN`
  - Value: `YOUR_ACTUAL_BOT_TOKEN_HERE`

## 5. Important: The "Sleep" Workaround
Because we are using a "Web Service" (to get it for free), Koyeb expects a port to be open. To prevent the bot from crashing, we need to add 3 lines of code to create a "Fake Web Server".

## 6. Deployment Command
Koyeb will automatically see your `Procfile` and run `python bot.py`.

---

### Alternative: Render.com
If you use **Render**, you must use a service like [cron-job.org](https://cron-job.org) to "ping" your bot URL every 10 minutes to keep it from sleeping.

### Recommendation
Start with **Koyeb**. It is significantly faster and more stable for Python bots.
