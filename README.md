# The Ultimate File Converter Bot 🚀

A professional-grade Telegram bot that handles your documents, images, videos, and web knowledge—all for **100% FREE** with no limitations!

## ✨ Features

### 📄 Document Powerhouse
- **Word ↔ PDF**: Seamlessly convert `.docx` to `.pdf` and back.
- **PDF Merge**: Combine multiple PDFs into one document (use `/merge`).
- **PDF Compress**: Reduce file size for easy sharing.
- **PDF to Images**: Convert each page of a PDF into a high-quality JPG.

### 🖼️ Image & Privacy
- **Metadata (EXIF) Stripper**: Remove sensitive location and device data from photos before sharing.
- **Background Remover**: Use AI to remove backgrounds from any image.
- **To PDF/PNG/Sticker**: Quick conversion to various formats and Telegram stickers.

### 🌐 Web & Knowledge
- **URL to PDF**: Send any link (news, blog, tutorial) and get a clean PDF of the webpage.
- **Wikipedia Summary**: First-page analysis of your PDFs to find related knowledge on Wikipedia.

### 🔳 Swiss Army Tools
- **QR Code Generator**: Send any text or link to instantly generate a scannable QR Code.
- **Video to GIF/MP3**: Turn videos into animated clips or extract high-quality music.

---

## 🛠️ Installation (Local)

1. **Install Python 3.8+**
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Required External Tools** (For Windows):
   - **wkhtmltopdf**: Download from [here](https://wkhtmltopdf.org/downloads.html) for URL to PDF to work.
   - **Tesseract OCR**: Download from [here](https://github.com/UB-Mannheim/tesseract/wiki) for Image to Text.
4. **Setup Token**: Paste your token in `.env`.
5. **Run**:
   ```bash
   python bot.py
   ```

## 🌍 Free Hosting Hint
You can host this for free on **Koyeb** or **Render**. Both support Python and provide enough resources for small-scale use of this bot.

---
*Powered by Python and Open Source.*
