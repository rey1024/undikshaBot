import pandas as pd
import os
import asyncio
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
)
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler,
    CallbackQueryHandler, CommandHandler, filters
)

# === Load data dari Excel ===
df = pd.read_excel('data_lulus.xlsx')
df['No_Registrasi'] = df['No_Registrasi'].astype(str)
registrasi_map = dict(zip(df['No_Registrasi'], df['Nama']))

verified_users = {}  # user_id: True
verified_file = 'verified_users.csv'
BOT_TOKEN = '1155987649:AAHLKUo9AkUNFEtSKoJgz4m20femxejdP5o'  # Ganti token BotFather
txtVerifikasi="🔒 Anda diberikan waktu 5 menit untuk verifikasi, siapkan no peserta SNBP. Jika tidak verifikasi maka akan dikeluarkan dari grup ini."





def get_verif_message(user_name):
    return f"Halo {user_name}, selamat datang! Saya UndikshaBot, penjaga ketertiban grup ini 👮🏻🚔\nSilakan klik tombol di bawah dan kirim nomor registrasi untuk verifikasi. Siapkan nomor SNBP. \n Anda diberikan waktu 10 menit untuk verifikasi. Jika tidak maka anda akan dikeluarkan dari grup ini. Pastikan menggunakan nama sesuai nama asli anda (lengkap)"

# === Anggota baru masuk grup ===
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        chat_id = update.effective_chat.id
        user_id = member.id
        user_name = member.first_name

        # Batasi chatting
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False)
        )

        # Kirim tombol verifikasi
        keyboard = [[InlineKeyboardButton("Verifikasi Sekarang!", callback_data=f"verify_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=get_verif_message(user_name),
            reply_markup=reply_markup
        )

        # Auto kick jika tidak verifikasi
        await asyncio.sleep(600)
        if not verified_users.get(user_id, False):
            await context.bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
            await context.bot.send_message(chat_id=chat_id, text=f"{user_name} dikeluarkan karena tidak verifikasi.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data.startswith("verify_") and data.split("_")[1] == str(user_id):
        if verified_users.get(user_id, False):
            await query.answer()
            await query.message.reply_text("✅ Anda sudah terverifikasi.")
        else:
            await query.answer()
            await query.message.reply_text("Silakan kirim nomor SNBP Anda.")
            # Simpan flag
            context.chat_data[user_id] = {'awaiting_verification': True}

async def verify_nomor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    nomor = update.message.text.strip()

    # ✅ Cek apakah user sedang proses verifikasi
    is_waiting = context.chat_data.get(user_id, {}).get('awaiting_verification', False)
    if not is_waiting:
        return  # ❌ Abaikan semua pesan lainnya

    # Verifikasi lanjut
    chat_id = update.effective_chat.id

    if nomor in registrasi_map:
        nama_peserta = registrasi_map[nomor]
        verified_users[user_id] = True
        save_verified(user_id, nomor, nama_peserta)

        # Buka akses chat
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status != 'creator':
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=True)
            )

        await update.message.reply_text(f"✅ Verified! Selamat bergabung di Undiksha, {nama_peserta} 🎓")

        # Cek nama
        current_name = update.message.from_user.full_name.lower()
        expected_name = nama_peserta.lower()
        if expected_name not in current_name:
            try:
                await update.message.reply_text(
                    f"⚠️ Nama akun Anda berbeda.\n"
                    f"Data: {nama_peserta}\nAkun: {update.message.from_user.full_name}\n"
                    f"Silakan ubah nama jadi: {nama_peserta}\n"
                )

            except:
                await update.message.reply_text("⚠️ Tidak bisa kirim DM. Silakan chat bot ini.")

        # Hapus flag
        context.chat_data[user_id]['awaiting_verification'] = False
    else:
        await update.message.reply_text("❌ Nomor tidak ditemukan.")


# === Simpan hasil verifikasi ===
def save_verified(user_id, nomor, nama_peserta):
    new_row = pd.DataFrame([{'user_id': user_id, 'No_Registrasi': nomor, 'Nama': nama_peserta}])

    if os.path.exists(verified_file):
        df = pd.read_csv(verified_file)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row

    df.to_csv(verified_file, index=False)


# === Respon jika bot di-mention ===
VERIFIKASI_TOPIC_ID = 87  # Ganti dengan ID topic hasil print

async def command_verifikasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.message_thread_id)
    #if update.message.message_thread_id != VERIFIKASI_TOPIC_ID:
    #    return  # Abaikan jika bukan di topic verifikasiSNBP

    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat_id

    if verified_users.get(user_id, False):
        await update.message.reply_text("✅ Anda sudah terverifikasi.")
    else:
        keyboard = [[InlineKeyboardButton("Verifikasi Sekarang!", callback_data=f"verify_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=get_verif_message(user_name),
            reply_markup=reply_markup,
            message_thread_id=update.message.message_thread_id  # Balas di topic sama
        )


def load_verified_users():
    if os.path.exists(verified_file):
        df = pd.read_csv(verified_file)
        for _, row in df.iterrows():
            verified_users[int(row['user_id'])] = True

# === Jalankan bot ===
if __name__ == "__main__":
    load_verified_users()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Tangkap SEMUA teks, proses hanya jika user dalam proses verifikasi
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_nomor))

    app.add_handler(CommandHandler("verifikasi", command_verifikasi))



    print("Bot verifikasi siap! 🔑")
    app.run_polling()
