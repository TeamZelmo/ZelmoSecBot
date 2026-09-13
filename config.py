# -----------------------------------------
# CONFIGURATION FILE
# Yahan apni details bharein
# -----------------------------------------

# BotFather se mila hua bot token
BOT_TOKEN = "8836762588:AAH-TedOWd_tdtISJsQA7-yv2AOI6LOMq8s"

# Aapke bot ka username (@ ke bina), jaise "my_verify_bot"
# Yeh DM deep-link banane ke liye zaroori hai (Verify button ke liye)
BOT_USERNAME = "ZelmoSecBot"

# Sabhi required channels ki list
# id: channel ka numeric ID (jaise -1001234567890) ya "@username"
# title: display ke liye naam
# link: join karne ka public link (t.me/xxxx ya invite link)
#
# NOTE: Bot in sabhi channels me ADMIN hona chahiye
# (taaki wo get_chat_member call kar sake), warna check fail hoga.

CHANNELS = [
    {
        "id": "@ZelmoApex",
        "title": "Zelmo Apex | OTT Shop",
        "link": "https://t.me/ZelmoApex",
    },
    {
        "id": "@ZelmoStock",
        "title": "Zelmo Stock | OTT Shop",
        "link": "https://t.me/ZelmoStock",
    },
    {
        "id": "@zelmoreview",
        "title": "Zelmo Review | OTT Shop",
        "link": "https://t.me/zelmoreview",
    },
    {
        "id": "@zelmoproof",
        "title": "Zelmo Proof | OTT Shop",
        "link": "https://t.me/zelmoproof",
    },
    # Jitne chahiye utne channels yahan add karte jaayein
]
