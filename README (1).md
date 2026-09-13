# Force-Subscribe Telegram Bot (Hindi Guide)

Yeh bot group me un users ko roke ga jo aapke required channels join nahi kiye hain.

## Yeh Bot Kya Karta Hai

1. Group me koi bhi message kare
2. Bot check karta hai ki wo user sabhi listed channels me joined hai ya nahi
3. **Agar joined nahi hai:**
   - Uska message delete ho jata hai
   - User group me mute ho jata hai
   - Group me ek chhota sa message aata hai: "**{user}**, aap verified nahi
     ho" + sirf ek **"✅ Verify Karein"** button
4. User jab is button ko dabata hai to bot ki **DM (private chat)** khul
   jati hai, jahan sabhi channels ke join-links + ek
   **"✅ Maine Join Kar Liya"** button dikhta hai
5. User sabhi channels join karke DM me us button ko dabata hai:
   - Bot dobara check karta hai
   - Agar sab join ho gaye → us group me user **unmute** ho jata hai
   - Agar abhi bhi koi channel baaki hai → DM me hi bata diya jata hai

## Setup Steps

### 1. Bot Banayein
- Telegram par **@BotFather** ko message karein
- `/newbot` command bhejein aur naam/username set karein
- Aapko ek **BOT_TOKEN** milega, use save kar lein

### 2. Files Download Karein
Is folder me 3 files hain:
- `bot.py` — main code
- `config.py` — settings (yahan token aur channels dalne hain)
- `requirements.txt` — zaroori libraries

### 3. Config Bharein
`config.py` file kholein aur:
- `BOT_TOKEN` me apna token dalein
- `BOT_USERNAME` me apne bot ka username dalein (bina `@` ke), jaise
  `my_verify_bot` — is se "Verify Karein" button DM khol payega
- `CHANNELS` list me apne sabhi channels ka `id` (ya `@username`), `title`,
  aur `link` dalein

Example:
```python
CHANNELS = [
    {
        "id": "@mychannel",
        "title": "My Awesome Channel",
        "link": "https://t.me/mychannel",
    },
]
```

### 4. Bot ko Permissions Dena (SABSE ZAROORI STEP)
- Bot ko apne **Group** me add karke **Admin** banayein
  - Zaroori admin rights: **Delete Messages**, **Ban/Restrict Users**
- Bot ko apne **har ek Channel** me bhi add karke **Admin** banayein
  - (Sirf "member list dekhne" ki permission bhi kaafi hai, lekin post
    karne ki zaroorat nahi)

Agar bot channel me admin nahi hoga to wo check nahi kar payega ki user
joined hai ya nahi.

**Ek aur zaroori setting:** @BotFather me jaakar apne bot ke liye
`/setprivacy` command se **Privacy Mode OFF** kar dein, warna bot group ke
sabhi messages nahi dekh payega. Isse bot group ke normal messages padh
sakega taaki wo check kar sake ki user verified hai ya nahi.

### 5. Install & Run
Terminal/CMD me:

```bash
pip install -r requirements.txt
python bot.py
```

Bas! Ab bot chalu ho gaya hai.

## Hosting (24/7 chalane ke liye)
Apne computer ko hamesha on rakhna practical nahi hota, isliye bot ko
kisi server par host karein, jaise:
- **Railway.app**
- **Render.com**
- Koi bhi **VPS** (jaise DigitalOcean, AWS EC2) jahan `python bot.py`
  hamesha chalta rahe (screen/tmux ya systemd service ke saath)

## Optional Improvements (agar chahiye to bata dijiye)
- Naye member group join karte hi turant mute kar dena (jab tak wo channels
  join na kar le)
- Group admins ko is check se exclude karna
- Har channel ke liye alag-alag error message
- Database me track karna ki kaun kaun already verified hai (taaki bar-bar
  check na karna pade — API calls bachte hain)
