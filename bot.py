import os
import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from PIL import Image
from dotenv import load_dotenv

# Third-party conversion libraries
import wikipedia
import pdfkit
import qrcode
from gtts import gTTS
from pypdf import PdfReader, PdfWriter
import pytesseract
from rembg import remove
from pdf2docx import Converter
import img2pdf
from moviepy import VideoFileClip
from docx2pdf import convert

# Load environment variables
load_dotenv()
TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TEMP_DIR = "temp_files"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Verification Storage
VERIFIED_FILE = "verified_users.txt"
if not os.path.exists(VERIFIED_FILE):
    with open(VERIFIED_FILE, "w") as f: pass

# Configure external tool paths (Windows fallback)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def is_verified(user_id: int) -> bool:
    """Checks if a user is in the verified storage."""
    if not os.path.exists(VERIFIED_FILE):
        return False
    with open(VERIFIED_FILE, "r") as f:
        verified = [line.strip() for line in f.readlines()]
    return str(user_id) in verified

def mark_verified(user_id: int) -> None:
    """Adds a user to the verified storage."""
    user_id_str = str(user_id)
    if not is_verified(user_id):
        with open(VERIFIED_FILE, "a") as f:
            f.write(f"{user_id_str}\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and verification gate."""
    user_id = update.effective_user.id
    if is_verified(user_id):
        await update.message.reply_text(
            "🚀 *Welcome to the Ultimate Converter!*\n\n"
            "The bot is fully unlocked! Send me any file, image, or link to begin.",
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("Facebook 👍", url="https://www.facebook.com/nobojit.majumder.2024")],
            [InlineKeyboardButton("Instagram 📸", url="https://www.instagram.com/mr_nobojit.m/")],
            [InlineKeyboardButton("TikTok 🎵", url="https://www.tiktok.com/@nobojitnexus")],
            [InlineKeyboardButton("YouTube 📺", url="https://www.youtube.com/@NobojitNexus")],
            [InlineKeyboardButton("✅ I HAVE FOLLOWED & SUBSCRIBED", callback_data="verify_me")]
        ]
        await update.message.reply_text(
            "🔒 *Verification Required!*\n\n"
            "To use this bot for free forever, please follow and subscribe to my profiles below:\n\n"
            "Once done, click the **Verify** button to unlock all features!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages for URL conversion, PDF splitting, or TTS."""
    if not is_verified(update.effective_user.id):
        await start(update, context)
        return
    
    text = update.message.text.strip()
    
    # Range Split Detection (e.g. "1-5")
    if '-' in text and text.replace('-', '').isdigit():
        await handle_split(update, context)
        return

    # URL Detection
    if text.startswith('http://') or text.startswith('https://'):
        await handle_url(update, context)
        return
    
    # Text-to-Speech (TTS)
    msg = await update.message.reply_text("Converting text to speech... 🗣️")
    voice_path = os.path.join(TEMP_DIR, f"{update.message.message_id}_voice.ogg")
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(voice_path)
        with open(voice_path, 'rb') as f:
            await context.bot.send_voice(chat_id=update.message.chat_id, voice=f, caption="Here is your audio! 🎙️")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"TTS Error: {e}")
    finally:
        if os.path.exists(voice_path): os.remove(voice_path)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Converts a webpage URL to a PDF."""
    url = update.message.text.strip()
    msg = await update.message.reply_text("Capturing webpage... 🌐")
    output_path = os.path.join(TEMP_DIR, f"{update.message.message_id}_web.pdf")
    try:
        options = {'page-size': 'A4', 'quiet': ''}
        if os.path.exists(WKHTMLTOPDF_PATH):
            config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
            pdfkit.from_url(url, output_path, configuration=config, options=options)
        else:
            pdfkit.from_url(url, output_path, options=options)
            
        with open(output_path, 'rb') as f:
            await context.bot.send_document(chat_id=update.message.chat_id, document=f)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"Capture failed: {e}")
    finally:
        if os.path.exists(output_path): os.remove(output_path)

async def handle_split(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Splits a PDF based on a provided page range."""
    input_path = context.user_data.get('current_file')
    if not input_path or not input_path.lower().endswith('.pdf'):
        await generate_qr(update, context)
        return

    try:
        pages_range = update.message.text.split('-')
        start_pg, end_pg = int(pages_range[0])-1, int(pages_range[1])
        
        msg = await update.message.reply_text(f"Extracting pages {start_pg+1} to {end_pg}... ✂️")
        output_path = os.path.join(TEMP_DIR, "split.pdf")
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for i in range(start_pg, min(end_pg, len(reader.pages))):
            writer.add_page(reader.pages[i])
            
        with open(output_path, "wb") as f: 
            writer.write(f)
        with open(output_path, 'rb') as f:
            await context.bot.send_document(chat_id=update.message.chat_id, document=f, caption="Pages extracted! ✅")
        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"Split Error: {e}")
    finally:
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates a QR code from text."""
    text = update.message.text.strip()
    qr_path = os.path.join(TEMP_DIR, f"{update.message.message_id}_qr.png")
    try:
        img = qrcode.make(text)
        img.save(qr_path)
        with open(qr_path, 'rb') as f:
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=f, caption="QR Code Generation Success! 🔳")
    except Exception as e:
        logger.error(f"QR Error: {e}")
    finally:
        if os.path.exists(qr_path): os.remove(qr_path)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes uploaded documents."""
    if not is_verified(update.effective_user.id):
        await start(update, context)
        return
        
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    file_ext = os.path.splitext(file_name)[1].lower()
    file_path = os.path.join(TEMP_DIR, f"{update.message.message_id}_{file_name}")
    
    await file.download_to_drive(file_path)
    context.user_data['current_file'] = file_path

    keyboard = []
    if file_ext == '.pdf':
        keyboard.append([InlineKeyboardButton("📄 to Word", callback_data="to_docx"), InlineKeyboardButton("📖 Wiki Info", callback_data="wiki_summary")])
        keyboard.append([InlineKeyboardButton("🖼️ to Images", callback_data="to_images"), InlineKeyboardButton("📉 Compress", callback_data="compress_pdf")])
        keyboard.append([InlineKeyboardButton("✂️ Split PDF", callback_data="split_hint")])
    elif file_ext == '.docx':
        keyboard.append([InlineKeyboardButton("📕 to PDF", callback_data="docx_to_pdf")])
    
    if keyboard:
        await update.message.reply_text(f"Options for {file_name}:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes uploaded photos."""
    if not is_verified(update.effective_user.id):
        await start(update, context)
        return
        
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = os.path.join(TEMP_DIR, f"{photo.file_id}.jpg")
    await file.download_to_drive(file_path)
    context.user_data['current_file'] = file_path
    
    keyboard = [
        [InlineKeyboardButton("📕 to PDF", callback_data="to_pdf"), InlineKeyboardButton("🔍 OCR (Text)", callback_data="ocr")],
        [InlineKeyboardButton("✨ Remove BG", callback_data="remove_bg"), InlineKeyboardButton("🛡️ Strip Meta", callback_data="strip_metadata")],
        [InlineKeyboardButton("🖼️ PNG", callback_data="to_png"), InlineKeyboardButton("🎭 Sticker", callback_data="to_sticker")]
    ]
    await update.message.reply_text("Image Tools Dashboard:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes uploaded videos."""
    if not is_verified(update.effective_user.id):
        await start(update, context)
        return
        
    video = update.message.video
    file = await video.get_file()
    file_path = os.path.join(TEMP_DIR, f"{video.file_id}.mp4")
    await file.download_to_drive(file_path)
    context.user_data['current_file'] = file_path
    
    keyboard = [[InlineKeyboardButton("📽️ to GIF", callback_data="to_gif"), InlineKeyboardButton("🎵 to MP3", callback_data="to_mp3")]]
    await update.message.reply_text("Video Processing Options:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all button interactions."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "verify_me":
        mark_verified(user_id)
        await query.edit_message_text(
            "🎉 *Welcome to the Family!*\n\n"
            "You are now verified. All pro features are unlocked! Send me a file to start converting.",
            parse_mode='Markdown'
        )
        return

    if not is_verified(user_id):
        await query.edit_message_text("❌ Please use /start and follow the instructions to unlock the bot.")
        return

    input_path = context.user_data.get('current_file')
    if not input_path or not os.path.exists(input_path):
        await query.edit_message_text("⚠️ File missing. Please upload the file again.")
        return

    action = query.data
    output_path = ""
    try:
        await query.edit_message_text("Processing your request... ⚙️")
        
        if action == "split_hint":
            await query.edit_message_text("✂️ *PDF Splitter:* Send the page range like `1-5` to extract those pages.", parse_mode='Markdown')
            return

        elif action == "ocr":
            text = pytesseract.image_to_string(Image.open(input_path))
            results = f"📝 *Extracted Text:*\n\n`{text[:4000]}`" if text.strip() else "❌ No text found in image."
            await context.bot.send_message(chat_id=query.message.chat_id, text=results, parse_mode='Markdown')
            await query.delete_message(); return

        elif action == "remove_bg":
            output_path = input_path.rsplit('.', 1)[0] + "_nobg.png"
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o: 
                    o.write(remove(i.read()))

        elif action == "wiki_summary":
            reader = PdfReader(input_path)
            first_page = reader.pages[0].extract_text()[:100] if reader.pages else ""
            search_query = first_page.split('\n')[0].strip() or os.path.basename(input_path)
            try:
                wiki_title = wikipedia.suggest(search_query) or search_query
                summary = wikipedia.summary(wiki_title, sentences=5)
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"📖 *Wiki Summary:* {wiki_title}\n\n{summary}")
            except Exception: 
                await query.edit_message_text("❌ No relevant Wikipedia data found for this document.")
            await query.delete_message(); return

        elif action == "to_docx":
            output_path = input_path.rsplit('.', 1)[0] + ".docx"
            cv = Converter(input_path); cv.convert(output_path); cv.close()
        
        elif action == "docx_to_pdf":
            output_path = input_path.rsplit('.', 1)[0] + ".pdf"
            convert(input_path, output_path)

        elif action == "to_pdf":
            output_path = input_path.rsplit('.', 1)[0] + ".pdf"
            with open(output_path, "wb") as f: 
                f.write(img2pdf.convert(input_path))

        elif action == "to_gif":
            output_path = input_path.rsplit('.', 1)[0] + ".gif"
            clip = VideoFileClip(input_path).subclip(0, 10); clip.write_gif(output_path, fps=10); clip.close()

        elif action == "to_mp3":
            output_path = input_path.rsplit('.', 1)[0] + ".mp3"
            clip = VideoFileClip(input_path); clip.audio.write_audiofile(output_path); clip.close()

        elif action == "strip_metadata":
            output_path = input_path.rsplit('.', 1)[0] + "_safe.jpg"
            img = Image.open(input_path)
            clean = Image.new(img.mode, img.size)
            clean.putdata(list(img.getdata()))
            clean.save(output_path, "JPEG")

        if output_path and os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                await context.bot.send_document(chat_id=query.message.chat_id, document=f, caption="Here is your converted file! ✅")
            os.remove(output_path)
        await query.delete_message()

    except Exception as e:
        await query.edit_message_text(f"❌ *Error during conversion:* {e}", parse_mode='Markdown')
    finally:
        if input_path and os.path.exists(input_path):
            try: os.remove(input_path)
            except Exception: pass

if __name__ == '__main__':
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🚀 Bot is LIVE and optimized! 0 Errors Expected.")
    app.run_polling()
