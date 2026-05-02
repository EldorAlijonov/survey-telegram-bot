# Telegram Survey Bot

Ta'lim tashkilotlari o'quvchilari uchun zamonaviy kasblarga qiziqishni aniqlaydigan Telegram bot. Userlar ro'yxatdan o'tadi, so'rovnomani to'ldiradi va aktiv majburiy kanal bo'lsa obunadan o'tadi. Adminlar statistika ko'radi, foydalanuvchilarni sanalar bo'yicha varaqlaydi, Excel eksport qiladi, admin qo'shadi, majburiy obuna kanalini boshqaradi va reklama yuboradi.

## O'rnatish

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## PostgreSQL yaratish

```sql
CREATE DATABASE survey_bot;
CREATE USER survey_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE survey_bot TO survey_user;
```

## .env sozlash

`.env.example` faylidan `.env` yarating va qiymatlarni to'ldiring:

```env
BOT_TOKEN=telegram_bot_token
DATABASE_URL=postgresql+asyncpg://survey_user:strong_password@localhost:5432/survey_bot
MAIN_ADMIN_IDS=111111111,222222222
LOG_LEVEL=INFO
PAGE_SIZE=5
```

`MAIN_ADMIN_IDS` ichidagi ID lar asosiy admin hisoblanadi. Faqat ular yangi admin qo'sha oladi yoki adminni o'chira oladi.

## Majburiy obuna kanalini sozlash

Botni ommaviy Telegram kanalga admin qilib qo'shing. Keyin admin paneldagi `📢 Majburiy obuna` bo'limidan kanal username yoki havolasini yuboring. Username `@channel_username`, `channel_username`, `https://t.me/channel_username`, `http://t.me/channel_username` yoki `t.me/channel_username` ko'rinishida bo'lishi mumkin. Kanal nomi Telegram'dan avtomatik olinadi. Bot kanal public ekanini va o'zi admin ekanini tekshiradi. Aktiv kanal bo'lmasa, user so'rovnomani obuna tekshiruvisiz yakunlaydi.

## Migration

```bash
alembic upgrade head
```

## Botni ishga tushirish

```bash
python main.py
```

## Docker Compose

```bash
docker compose up --build -d
```

Docker Compose PostgreSQL konteynerini ko'taradi, migrationni ishlatadi va botni ishga tushiradi.

## Serverda ishga tushirish

`nohup`:

```bash
nohup python main.py > bot.log 2>&1 &
```

`pm2`:

```bash
pm2 start "python main.py" --name survey-bot
pm2 save
```

## Asosiy buyruqlar

```bash
pip install -r requirements.txt
alembic upgrade head
python main.py
```
