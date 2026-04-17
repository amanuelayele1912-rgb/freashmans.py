import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ቦት መለያ (Token) ---
TOKEN = '8793360624:AAGNnMl7RffZTCkD3LMiac_XmksieN0gG9o'

# --- የፋይል መዝገብ (File IDs) ---
# እዚህ ጋር ቦቱ የሚሰጥህን ረጅም ID ቁጥር በእያንዳንዱ ስም ፊት ለፊት ባለው ባዶ ቦታ (引号) ውስጥ ተካ።
FILE_DATABASE = {
    # Semester 1
    "Maths_Module": "", "Maths_Mid": "", "Maths_Final": "", "Maths_PPT": "",
    "Logic_Module": "", "Logic_Mid": "", "Logic_Final": "", "Logic_PPT": "",
    "Psychology_Module": "", "Psychology_Mid": "", "Psychology_Final": "", "Psychology_PPT": "",
    "Geography_Module": "", "Geography_Mid": "", "Geography_Final": "", "Geography_PPT": "",
    "English I_Module": "", "English I_Mid": "", "English I_Final": "", "English I_PPT": "",
    "Economics_Module": "", "Economics_Mid": "", "Economics_Final": "", "Economics_PPT": "",
    "Sport_Module": "", "Sport_Mid": "", "Sport_Final": "", "Sport_PPT": "",
    "Critical Thinking_Module": "", "Critical Thinking_Mid": "", "Critical Thinking_Final": "", "Critical Thinking_PPT": "",
    
    # Semester 2
    "Anthropology_Module": "", "Anthropology_Mid": "", "Anthropology_Final": "", "Anthropology_PPT": "",
    "Inclusive_Module": "", "Inclusive_Mid": "", "Inclusive_Final": "", "Inclusive_PPT": "",
    "Global Trend_Module": "", "Global Trend_Mid": "", "Global Trend_Final": "", "Global Trend_PPT": "",
    "History_Module": "", "History_Mid": "", "History_Final": "", "History_PPT": "",
    "English II_Module": "", "English II_Mid": "", "English II_Final": "", "English II_PPT": "",
    "Entrepreneurship_Module": "", "Entrepreneurship_Mid": "", "Entrepreneurship_Final": "", "Entrepreneurship_PPT": "",
    "Emerging Tech_Module": "", "Emerging Tech_Mid": "", "Emerging Tech_Final": "", "Emerging Tech_PPT": "",
    "Civics_Module": "", "Civics_Mid": "", "Civics_Final": "", "Civics_PPT": ""
}

# ትምህርቶችን መለየት
SUBJECTS = {
    "1": ["Maths", "Logic", "Psychology", "Geography", "English I", "Economics", "Sport", "Critical Thinking"],
    "2": ["Anthropology", "Inclusive", "Global Trend", "History", "English II", "Entrepreneurship", "Emerging Tech", "Civics"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔹 Semester 1", callback_data='sem_1')],
        [InlineKeyboardButton("🔹 Semester 2", callback_data='sem_2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "እንኳን ወደ Freshman መርጃ ቦት መጡ! 👋\nእባክዎ ሴሚስተርዎን ይምረጡ፦"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('sem_'):
        sem_num = data.split('_')[1]
        subjects = SUBJECTS[sem_num]
        keyboard = []
        for i in range(0, 8, 2):
            row = [
                InlineKeyboardButton(subjects[i], callback_data=f"sub_{sem_num}_{subjects[i]}"),
                InlineKeyboardButton(subjects[i+1], callback_data=f"sub_{sem_num}_{subjects[i+1]}")
            ]
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 ተመለስ", callback_data='main_menu')])
        await query.edit_message_text(f"የ Semester {sem_num} ትምህርቶች፦", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith('sub_'):
        _, sem_num, sub_name = data.split('_')
        keyboard = [
            [InlineKeyboardButton("📖 Module", callback_data=f'file_{sub_name}_Module'),
             InlineKeyboardButton("📝 Mid Exam", callback_data=f'file_{sub_name}_Mid')],
            [InlineKeyboardButton("🎯 Final Exam", callback_data=f'file_{sub_name}_Final'),
             InlineKeyboardButton("📊 PPT (Reading)", callback_data=f'file_{sub_name}_PPT')],
            [InlineKeyboardButton("🔙 ተመለስ", callback_data=f'sem_{sem_num}')]
        ]
        await query.edit_message_text(f"ለ {sub_name} የሚፈልጉትን ይምረጡ፦", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith('file_'):
        _, sub, f_type = data.split('_')
        file_key = f"{sub}_{f_type}"
        
        if file_key in FILE_DATABASE and FILE_DATABASE[file_key] != "":
            await query.message.reply_document(document=FILE_DATABASE[file_key], caption=f"ይህ የ {sub} {f_type} ፋይል ነው።")
        else:
            await query.message.reply_text(f"ይቅርታ፣ የ {sub} {f_type} ፋይል ገና አልተጫነም ወይም ID አልተሰጠውም።")

    elif data == 'main_menu':
        await start(update, context)

# ፋይል ስትልክ ID እንዲነግርህ
async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        fid = update.message.document.file_id
        fname = update.message.document.file_name
        await update.message.reply_text(f"✅ ፋይል ተቀብያለሁ!\nስም: {fname}\n\nID (ይህንን ኮፒ አድርገህ ኮዱ ውስጥ አስገባ)፦\n`{fid}`", parse_mode='MarkdownV2')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.add_handler(MessageHandler(filters.Document.ALL, get_file_id))
    
    print("Freshman ቦት ስራ ጀምሯል... ፋይሎችን ለቦቱ መላክ ትችላለህ።")
    app.run_polling()
