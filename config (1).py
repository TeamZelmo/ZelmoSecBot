# -----------------------------------------
# CONFIGURATION FILE
# Yahan apni details bharein
# -----------------------------------------

# BotFather se mila hua bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Aapke bot ka username (@ ke bina), jaise "my_verify_bot"
# Yeh DM deep-link banane ke liye zaroori hai (Verify button ke liye)
BOT_USERNAME = "YOUR_BOT_USERNAME_HERE"

# Sabhi required channels ki list
# id: channel ka numeric ID (jaise -1001234567890) ya "@username"
# title: display ke liye naam
# link: join karne ka public link (t.me/xxxx ya invite link)
#
# NOTE: Bot in sabhi channels me ADMIN hona chahiye
# (taaki wo get_chat_member call kar sake), warna check fail hoga.

CHANNELS = [
    {
        "id": "@your_channel_1",
        "title": "Channel 1",
        "link": "https://t.me/your_channel_1",
    },
    {
        "id": "@your_channel_2",
        "title": "Channel 2",
        "link": "https://t.me/your_channel_2",
    },
    # Jitne chahiye utne channels yahan add karte jaayein
]
