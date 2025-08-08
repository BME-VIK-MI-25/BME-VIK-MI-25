from prisma import Client
import prisma 
async def InsertBannedWord(word: str):
    try:
        client = Client()    
        await client.connect()    
        await client.blacklistedwords.create(
            data = {
                word: word
            }
        )
        return True
    except prisma.errors.DataError:
        return "Hibás adatok, a beszúrás nem történt meg."
    except prisma.errors.ClientNotConnectedError:
        return "Kapcsolódási hiba, a beszúrás nem történt meg."

async def GetBannedWordList():
    client = Client()    
    await client.connect()    
    result = await client.blacklistedwords.find_many()
    words = [res.word for res in result]
    return words

async def RemoveBannedWord(word: str):
    client = Client()    
    await client.connect()    
    await client.blacklistedwords.delete(
        where = {
            word: word
        }
    )
    return

async def CheckBannedWord(message: str):
    banned_words = GetBannedWordList()
    for word in banned_words:
        if word in message:
            return True
    return False
