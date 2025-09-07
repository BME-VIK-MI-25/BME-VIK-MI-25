from data.db import banned_words
from data.db import moderationDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
banned_words_file = BASE_DIR / "data" / "banned_words.txt"

async def InsertBannedWords(words: list[str]) -> None:
    word_list = words.split(',')
    for word in word_list:
        word = word.strip()
        if word not in banned_words:
            with open(banned_words_file, 'a') as f:
                f.write(f"{word}\n")
            banned_words.append(word)
    
async def InsertBannedWord(word: str) -> None:
    if word not in banned_words:
        with open(banned_words_file, 'a') as f:
            f.write(f"{word}\n")
        banned_words.append(word)


async def GetBannedWordList() -> list[str]:
    return banned_words

async def RemoveBannedWord(word: str) -> None:
    if word in banned_words:
        banned_words.remove(word)
        with open(banned_words_file, 'w') as f:
            for line in banned_words:
                    f.write(f"{line}\n")

async def CheckBannedWord(message: str, userId: int) -> bool:
    for word in banned_words:
        if word in message.content:
            if moderationDict.get(userId) is not None:
                moderationDict[userId]['bannedCount'] += 1
            else:
                moderationDict[userId] = {'bannedCount': 1, 'inviteBanExpiry': None}
            return True
    return False

async def GetBannedWordCount(userId: int) -> int:
    if moderationDict.get(userId) is not None:
        return moderationDict[userId]['bannedCount']
    return 0

async def UpdateBanExpiry(user_id: int, ban_expiry) -> None:
    moderationDict[user_id]['inviteBanExpiry'] = ban_expiry

async def GetBanExpiries() -> list[dict]:
    records_list = [{"userId": userId, **info} for userId, info in moderationDict.items()]
    return records_list

async def DeleteBanExpiry(user_id: int) -> None:
    if moderationDict.get(user_id) is not None:
        moderationDict[user_id]['inviteBanExpiry'] = None
        moderationDict[user_id]['bannedCount'] = 0
