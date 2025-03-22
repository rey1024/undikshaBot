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
BOT_TOKEN = ''  # Ganti token BotFather
txtVerifikasi="🔒 Anda diberikan waktu 5 menit untuk verifikasi, siapkan no peserta SNBP. Jika tidak verifikasi maka akan dikeluarkan dari grup ini."





def get_verif_message(user_name):
    return f"Salam Harmoni, {user_name}!,  Saya UndikshaBot, penjaga ketertiban grup ini 👮🏻🚔\nSilakan klik tombol di bawah dan kirim nomor registrasi SNBP untuk verifikasi.\n Anda diberikan waktu 10 menit untuk verifikasi. \nJika tidak maka anda akan dikeluarkan dari grup ini. Pastikan menggunakan nama sesuai nama asli anda (lengkap)\nAnda hanya bisa mengirim chat setelah verifikasi!\n#UPATIK-UNDIKSHA"

# === Anggota baru masuk grup ===
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        chat_id = update.effective_chat.id
        user_id = member.id
        user_name = member.first_name

        # Batasi chatting
      #  await context.bot.restrict_chat_member(
     #       chat_id=chat_id,
       #     user_id=user_id,
        #    permissions=ChatPermissions(can_send_messages=False)
        #)

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
import random

# 🌟 Kata-kata mutiara pendidikan
education_quotes = [
    "📚 Belajar rajin janganlah malas,\nIlmu dicari penuh semangat.\nPendidikan itu sangatlah luas,\nBuka masa depan penuh berkat.",
    
    "🖋️ Ke kampus pagi membawa pena,\nDi tas tersimpan buku tebal.\nIlmu dikejar dengan gembira,\nKelak sukses bukanlah khayal.",
    
    "🚀 Bangun pagi semangat membara,\nMenuju kelas bawa harapan.\nJangan ragu belajar bersahaja,\nCita-cita pun pasti tercapai kemudian.",
    
    "🎓 Siang belajar malam menulis,\nMenghafal rumus tanpa lelah.\nIlmu itu bak pelita yang manis,\nTerangi hidup jauhi gelisah.",
    
    "🌟 Jalan ke pasar membeli pepaya,\nPulangnya mampir ke toko kue.\nIlmu dikejar sepanjang maya,\nAgar hidup penuh warna dan bahagia.",
    
    "🌱 Menanam benih di ladang subur,\nDisiram air pagi dan petang.\nIlmu itu tumbuh bersyukur,\nBawa berkah sepanjang hidup panjang.",
    
    "📖 Membaca buku di pagi cerah,\nMenyerap ilmu penuh semangat.\nDengan belajar kita berserah,\nKe masa depan penuh berkat.",
    
    "🎯 Pergi ke sekolah naik sepeda,\nBerjumpa teman penuh tawa.\nIlmu ditimba dari mereka,\nModal hidup sepanjang masa.",
    
    "💡 Cahaya terang datang menjelang,\nDari buku penuh hikmah.\nIlmu adalah kekuatan gemilang,\nMengubah dunia penuh berkah.",
    
    "🎼 Menyanyi riang di taman bunga,\nSuara merdu penuh suka.\nIlmu dipelajari jangan ditunda,\nAgar hidup tak hampa dan duka.",
    
    "📘 Buka buku jangan mengeluh,\nMeski tugas datang bertubi.\nPendidikan itu menumbuh,\nCita-cita pun kan diraih nanti.",
    
    "🏆 Kejar ilmu tak kenal lelah,\nTantangan hadapi dengan tabah.\nKelak kau raih sukses cerah,\nDengan usaha dan doa penuh berkah.",
    
    "📝 Tulis catatan jangan berhenti,\nUlang kaji tiada jemu.\nDengan tekun dan niat murni,\nIlmu bertambah, rejeki bertemu.",
    
    "🌈 Di pagi hari embun menetes,\nBurung bernyanyi bersahutan.\nBelajar giat tiada stres,\nMasa depan dalam genggaman.",
    
    "🚴‍♂️ Kayuh sepeda ke perpustakaan,\nMembaca buku tak kenal bosan.\nIlmu dicari penuh harapan,\nHidup indah tanpa beban.",
    
    "📚 Menulis puisi di buku tebal,\nDihias tinta penuh makna.\nIlmu dan amal jangan tinggal,\nBahagia hidup dunia akhiratnya.",
    
    "🕊️ Merpati terbang di langit biru,\nMencari makan tak kenal waktu.\nBelajar giat sejak dahulu,\nAgar kelak tak menyesal selalu.",
    
    "📜 Membaca syair penuh semangat,\nSambil minum teh hangat pagi.\nIlmu dicari jadi berkat,\nMasa depan pun makin berseri.",
    
    "🍃 Daun jatuh ke tanah basah,\nHujan deras turun ke bumi.\nBelajar itu janganlah resah,\nIlmu indah, bawa harmoni.",
    
    "🌞 Matahari terbit di ufuk timur,\nCahaya terang menyinari bumi.\nIlmu dicari jangan mundur,\nJadikan hidup penuh arti.",
    
    "🎨 Melukis mimpi di kanvas harapan,\nDengan kuas semangat membara.\nIlmu ditimba tanpa beban,\nMenggapai cita-cita mulia.",
    
    "💪 Duduk tenang di ruang kelas,\nMendengar guru penuh minat.\nIlmu dipelajari tanpa malas,\nJalan sukses terbuka lebat.",
    
    "🧠 Isi kepala dengan ilmu,\nPenuh semangat tiada henti.\nKelak kau jadi insan maju,\nMembawa perubahan sejati.",
    
    "🌾 Menanam padi di sawah luas,\nPagi hingga sore bersusah payah.\nBelajar giat membawa puas,\nKelak hidup penuh berkah.",
    
    "🎺 Bunyi terompet di pagi hari,\nMembangunkan semangat belajar lagi.\nDengan ilmu hidup berseri,\nJalan sukses takkan lari.",
    
    "🔭 Lihat bintang di malam sunyi,\nBerkhayal tinggi gapai mimpi.\nBelajar giat penuh arti,\nMasa depan tak lagi sepi.",
    
    "🏕️ Berkemah di hutan pinus,\nMembaca buku di api unggun.\nIlmu ditimba jangan putus,\nKelak bahagia penuh rukun.",
    
    "🧺 Menganyam bambu jadi tikar,\nDuduk tenang sambil belajar.\nIlmu itu bagaikan akar,\nMenopang hidup agar segar.",
    
    "🏞️ Melukis alam indah nian,\nGunung tinggi langit membiru.\nIlmu dituntut jadi pedoman,\nMembuka jalan baru yang seru.",
    
    "📂 Membuka catatan lama terjaga,\nMengulang pelajaran penuh makna.\nIlmu didapat bukan karena harta,\nTapi usaha dan semangat membara.",
    
    "⚙️ Mesin berputar menghasilkan tenaga,\nBelajar tekun penuh kerja.\nIlmu diserap sebagai bekal,\nMenuju hidup penuh sejahtera.",
    
    "🌅 Mentari pagi menyapa mesra,\nBangun tidur langsung belajar.\nIlmu itu tak pernah sia-sia,\nPasti kelak akan berfaedah.",
    
    "🪁 Main layang di lapang luas,\nBersama teman penuh tawa.\nIlmu dituntut jangan putus,\nDemi masa depan gemilang cerah.",
    
    "🎢 Hidup kadang naik kadang turun,\nBelajar tekun jangan mundur.\nIlmu bekal hidup makmur,\nMasa depan cerah pasti teratur.",
    
    "🧹 Menyapu halaman di pagi hari,\nMembersihkan hati untuk belajar.\nIlmu itu cahaya diri,\nMenerangi jalan tanpa gelisah.",
    
    "💼 Pergi kerja membawa bekal,\nIlmu jadi senjata andalan.\nBelajar giat penuh akal,\nSukses datang tanpa halangan.",
    
    "🪴 Menyiram bunga tiap pagi,\nMerawat tumbuh penuh kasih.\nIlmu dirawat jangan lalai,\nJadi manusia penuh bijak bestari.",
    
    "🧵 Menjahit baju dengan hati,\nSetiap jahitan penuh makna.\nBelajar itu pelita hati,\nTerangi hidup penuh cahaya.",
    
    "⛅ Awan berarak di langit biru,\nHujan turun membasahi rindu.\nBelajar tekun di waktu baru,\nIlmu tumbuh tanpa jemu.",
    
    "🛶 Mendayung sampan di sungai tenang,\nMenuju tujuan tanpa bimbang.\nIlmu itu bekal menang,\nMenjadi insan penuh gemilang.",
]


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

        quote = random.choice(education_quotes)
        await update.message.reply_text(
            f"✅ Verified! Selamat kamu sudah terverifikasi sebagai peserta lulus SNBP di Undiksha, \n{nama_peserta} 🎓\n\nPantun untukmu hari ini:\n{quote}",
            parse_mode="Markdown"
        )


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
        await update.message.reply_text("❌ Nomor pendaftaran tidak ditemukan, silakan ulangi!")


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
        await update.message.reply_text("✅ Anda sudah terverifikasi. Tidak perlu verifikasi lagi")
    else:
        keyboard = [[InlineKeyboardButton("Verifikasi Sekarang!", callback_data=f"verify_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=get_verif_message(user_name),
            reply_markup=reply_markup,
            message_thread_id=update.message.message_thread_id  # Balas di topic sama
        )
# Variasi status bot
status_messages = [
    "💡 Bot masih hidup dan on duty!",
    "✅ Bot aktif, tidak sedang rebahan.",
    "⚡ Aku siaga! Nggak akan AFK 💻",
    "📡 Bot connected... sinyal penuh!",
    "🔔 Saya masih bernapas... secara digital 🤖",
    "🛡️ Bot siap menjaga ketertiban grup!",
]

# Kata-kata lucu mahasiswa baru
funny_responses = [
    # Lucu-lucu 😆
    "Mahasiswa baru detected... sabar ya, daftar kembali itu perjuangan 💪",
    "Sabar ya dek yaaa, daftar ulang butuh perjuangan 😅",
    "Santai bestie, verifikasi lancar, masa depan cerah 🌈",
    "Tenang... bot ini lulus S2 Ke-bot-an 🤖🎓",
    "Verifikasi? Santai, nggak akan ditolak... kecuali salah nomor 😜",
    "Sabar... ngopi dulu ya 🧐",
    "Bot aktif, kamu juga harus aktif... verifikasi maksudnya 😆",
    "Kopi dulu, verifikasi belakangan... eh jangan, keburu di-kick! ☕🚪",
    "Dunia ini keras, masa depanmu cerah bersama Undiksha 💥",

    # Motivasi 🔥
    "📚 Hari ini daftarkembali, besok jadi mahasiswa berprestasi!",
    "🎯 Awali perjalananmu di Undiksha dengan semangat, sukses menantimu!",
    "💪 Setiap langkah kecil hari ini, menentukan pencapaian besarmu nanti.",
    "🌟 Jangan ragu, masa depan cerah sedang menantimu di Undiksha!",
    "🚀 Verifikasi sekarang, gapai cita-cita setinggi angkasa!",
    "🔥 Kamu adalah calon pemimpin masa depan. Mulai dari sini, dari Undiksha!",
]


# (Opsional) List stiker lucu - tambahkan ID stiker favoritmu
sticker_ids = [
    # Contoh ID stiker default Telegram
    "CAACAgUAAxkBAAEEe2JlkiXkHbZFLWJPVzKq7QQcZL1XrAACnQQAAhC6EVShxkyGxy7pQjAE",  # Bot love
    "CAACAgUAAxkBAAEEe2RlkiXLb4wzU8k7bnEpJADDCMxE9AACmwQAAhC6EVQ60v5ufgXt5jAE",  # Bot laugh
]

import random
async def command_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    status = random.choice(status_messages)
    joke = random.choice(funny_responses)
    sticker = random.choice(sticker_ids)

    # Kirim pesan lucu
    await update.message.reply_text(f"{status}\n\n{joke}")

    # Kirim stiker lucu (optional)
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)




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

    app.add_handler(CommandHandler("test", command_test))


    print("Bot verifikasi siap! 🔑")
    app.run_polling()
