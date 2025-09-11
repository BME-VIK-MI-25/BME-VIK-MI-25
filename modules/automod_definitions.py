from data.db import banned_words
from data.db import moderationDict
from pathlib import Path
from disnake import Message

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

async def RemoveBannedWord(word: str) -> None:
    if word in banned_words:
        banned_words.remove(word)
        with open(banned_words_file, 'w') as f:
            for line in banned_words:
                    f.write(f"{line}\n")

async def CheckBannedWord(message: Message, userId: int) -> bool:
    for word in banned_words:
        if word in message.content:
            for item in moderationDict.items():
                if item[0] is not None:
                    if item[0] == userId:
                        item[1][0]+=1
                else:
                    if item[0] == userId:
                        item[1][0] = 1
                        item[1][1] = None
                return True
    return False
            

async def GetBannedWordCount(userId: int) -> int:
    for item in list(moderationDict.items()):
        if item[0] is not None:
            return item[1][0]
        return 0

async def UpdateBanExpiry(user_id: int, ban_expiry) -> None:
    for item in list(moderationDict.items()):
        if item[0 == user_id]:
            item[1][1] = ban_expiry

async def GetBanExpiries() -> list[list]:
    records_list = []
    for item in list(moderationDict.items()):
        if item[0] is not None:
            records_list.append([item[0], item[1][1]])
    return records_list
        

async def DeleteBanExpiry(user_id: int) -> None:
    for item in list(moderationDict.items()):
        if item[0] is not None:
            if item[0] == user_id:
                item[1][0] = 0
                item[1][1] = None

if __name__ == "__main__":
    moderationDict = {123456789: [0, 0], 987654321: [2, 123456]} # userID -> int: [bannedCount -> int, inviteBanExpiry -> datetime]
    records_list = []
    for item in list(moderationDict.items()):
        if item[0] is not None:
            records_list.append([item[0], item[1][1]])
    print(records_list)