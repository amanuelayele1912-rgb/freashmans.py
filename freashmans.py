import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ቦት መለያ ---
TOKEN = '8793360624:AAGNnMl7RffZTCkD3LMiac_XmksieN0gG9o'
ADMIN_USERNAME = 'travellover719' 

# --- ዳታቤዝ ማዘጋጃ ---
def init_db():
    conn = sqlite3.connect('freshman_library.db')
    cursor = conn.cursor()
    # በትክክል 3 አምዶች (file_key, file_id, f_kind) እንዲኖሩት እናደርጋለን
    cursor.execute('CREATE TABLE IF NOT EXISTS files (file_key TEXT PRIMARY KEY, file_id TEXT, f_kind TEXT)')
    conn.commit()
    conn.close()

def save_file(key, fid, fkind):
    conn = sqlite3.connect('freshman_library.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO files VALUES (?, ?, ?)", (key, fid, fkind))
    conn.commit()
    conn.close()

def get_file_info(key):
    conn = sqlite3.connect('freshman_library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, f_kind FROM files WHERE file_key = ?", (key,))
    res = cursor.fetchone()
    conn.close()
    return res if res else (None, None)

SUBJECTS = {
    "1": ["Maths", "Logic", "Psychology", "Geography", "English I", "Economics", "Sport", "Critical Thinking"],
    "2": ["Anthropology", "Inclusive", "Global Trend", "History", "English II", "Entrepreneurship", "Emerging Tech", "Civics"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎓 Semester 1", callback_data='sem_1')],
                [InlineKeyboardButton("🎓 Semester 2", callback_data='sem_2')]]
    text = "እንኳን ወደ Freshman መርጃ ቦት መጡ! 📚\nእባክዎ ሴሚስተር ይምረጡ፦"
    if update.message: await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else: await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('sem_'):
        s_num = data.split('_')[1]
        subs = SUBJECTS[s_num]
        btns = [[InlineKeyboardButton(subs[i], callback_data=f"sub_{s_num}_{subs[i]}"),
                 InlineKeyboardButton(subs[i+1], callback_data=f"sub_{s_num}_{subs[i+1]}")] for i in range(0, 8, 2)]
        btns.append([InlineKeyboardButton("🔙 ተመለስ", callback_data='back_start')])
        await query.edit_message_text(f"የ Semester {s_num} ትምህርቶች፦", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith('sub_'):
        _, s_num, sub = data.split('_')
        btns = [[InlineKeyboardButton("📖 Module", callback_data=f'get_{sub}_Module'), InlineKeyboardButton("📝 Mid Exam", callback_data=f'get_{sub}_Mid')],
                [InlineKeyboardButton("🎯 Final Exam", callback_data=f'get_{sub}_Final'), InlineKeyboardButton("📊 PPT", callback_data=f'get_{sub}_PPT')],
                [InlineKeyboardButton("🔙 ተመለስ", callback_data=f'sem_{s_num}')]]
        await query.edit_message_text(f"ለ {sub} የሚፈልጉትን ይምረጡ፦", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith('get_'):
        _, sub, ftype = data.split('_')
        fid, fkind = get_file_info(f"{sub}_{ftype}")
        if fid:
            cap = f"✅ የ {sub} {ftype}"
            if fkind == 'photo': await query.message.reply_photo(photo=fid, caption=cap)
            elif fkind == 'video': await query.message.reply_video(video=fid, caption=cap)
            else: await query.message.reply_document(document=fid, caption=cap)
        else:
            await query.message.reply_text(f"⚠️ ይቅርታ፣ የ {sub} {ftype} ፋይል ገና አልተጫነም።")

    elif data == 'back_start': await start(update, context)

async def handle_admin_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username != ADMIN_USERNAME: return
    fid, fkind = None, None
    if update.message.document: fid, fkind = update.message.document.file_id, 'doc'
    elif update.message.photo: fid, fkind = update.message.photo[-1].file_id, 'photo'
    elif update.message.video: fid, fkind = update.message.video.file_id, 'video'
    if not fid: return
    context.user_data['tmp_fid'], context.user_data['tmp_kind'] = fid, fkind
    all_subs = SUBJECTS["1"] + SUBJECTS["2"]
    btns = [[InlineKeyboardButton(all_subs[i], callback_data=f"reg_{all_subs[i]}"),
             InlineKeyboardButton(all_subs[i+1], callback_data=f"reg_{all_subs[i+1]}")] for i in range(0, len(all_subs), 2)]
    await update.message.reply_text(f"📂 ፋይል ተቀብያለሁ! ይህ የየትኛው ትምህርት ነው?", reply_markup=InlineKeyboardMarkup(btns))

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith('reg_'):
        sub = data.split('_')[1]
        btns = [[InlineKeyboardButton("Module", callback_data=f"save_{sub}_Module"),
                 InlineKeyboardButton("Mid Exam", callback_data=f"save_{sub}_Mid")],
                [InlineKeyboardButton("Final Exam", callback_data=f"save_{sub}_Final"),
                 InlineKeyboardButton("PPT", callback_data=f"save_{sub}_PPT")]]
        await query.edit_message_text(f"ለ {sub} ምን አይነት ፋይል ነው?", reply_markup=InlineKeyboardMarkup(btns))
    elif data.startswith('save_'):
        _, sub, ftype = data.split('_')
        fid, fkind = context.user_data.get('tmp_fid'), context.user_data.get('tmp_kind')
        if fid:
            save_file(f"{sub}_{ftype}", fid, fkind)
            await query.edit_message_text(f"✅ የ {sub} {ftype} በስኬት ተመዝግቧል!")

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_navigation, pattern="^(sem_|sub_|get_|back_start)"))
    app.add_handler(CallbackQueryHandler(handle_registration, pattern="^(reg_|save_)"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_admin_media))
    print("ቦቱ በአዲስ መልክ ስራ ጀምሯል...")
    app.run_polling()
