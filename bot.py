import logging
import random
import os
import json
import urllib.request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from cv2 import VideoCapture, imwrite
import mediapipe as mp

load_dotenv()

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# source: https://developers.google.com/mediapipe/solutions/vision/face_detector/python#image
mp_options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.IMAGE)
detector = FaceDetector.create_from_options(mp_options)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

token = os.getenv('TELEGRAM_BOT_TOKEN')
api_base_url = 'https://mercados.ambito.com/dolar/informal/variacion'

async def cat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hi {update.effective_user.first_name}, have a cat')
    await update.message.reply_photo(f'https://cataas.com/cat/cute?q={random.randrange(100)}')

async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        api_url = f'{api_base_url}?q={random.randrange(100)}'
        res = urllib.request.urlopen(api_url).read()
        parsed = json.loads(res)
        compra = parsed["compra"].replace(',', '.')
        venta = parsed["venta"].replace(',', '.')
        avg = (float(compra) + float(venta)) / 2
        await update.message.reply_text(f'Compra={compra}, venta={venta}, promedio={avg}')
    except:
        await update.message.reply_text("¡Ups! Algo falló")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cam = VideoCapture(0)

    result, image = cam.read()
    if result:
        imwrite("aux.png", image)
        await update.message.reply_photo(open("aux.png", "rb"))
        mp_image = mp.Image.create_from_file('aux.png')
        face_detector_result = detector.detect(mp_image)
        for detection in face_detector_result.detections:
            await update.message.reply_text(f'Chances de jeta: {detection.categories[0].score}')
    else:
        await update.message.reply_text("¡Ups! Algo falló")
    
    cam.release()

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. I know 'cat' and 'dolar'.")

app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("cat", cat))
app.add_handler(CommandHandler("dolar", dolar))
app.add_handler(CommandHandler("foto", photo))
app.add_handler(MessageHandler(filters.COMMAND, unknown))
app.run_polling()
