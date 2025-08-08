from prisma import Client
import prisma 
async def InsertBannedWords(words: list[str]):
    try:
        client = Client()    
        await client.connect()    
        for el in words:
            await client.blacklistedwords.create(
                data = {
                    'word': el
                }
            )
        await client.disconnect()
        return True
    except prisma.errors.DataError:
        await client.disconnect()
        return "Hibás adatok, a beszúrás nem történt meg."
    except prisma.errors.ClientNotConnectedError:
        await client.disconnect()
        return "Kapcsolódási hiba, a beszúrás nem történt meg."
    
async def InsertBannedWord(word: str):
    try:
        client = Client()    
        await client.connect()    
        await client.blacklistedwords.create(
            data = {
                'word': word
            }
        )
        await client.disconnect()
        return True
    except prisma.errors.DataError:
        await client.disconnect()
        return "Hibás adatok, a beszúrás nem történt meg."
    except prisma.errors.ClientNotConnectedError:
        await client.disconnect()
        return "Kapcsolódási hiba, a beszúrás nem történt meg."

async def GetBannedWordList():
    client = Client()    
    await client.connect()    
    result = await client.blacklistedwords.find_many()
    words = [res.word for res in result]
    await client.disconnect()
    return words

async def RemoveBannedWord(word: str):
    client = Client()    
    await client.connect()    
    await client.blacklistedwords.delete(
        where = {
            'word': word
        }
    )
    await client.disconnect()
    return

async def CheckBannedWord(message: str, userId: int):
    banned_words = GetBannedWordList()
    for word in banned_words:
        if word in message:
            client = Client()    
            await client.connect()   
            res = client.blacklistedwordcounter.find_first(where = {
                'userId': userId
            }) 
            exists = len(res) == 1
            if exists:
                client.blacklistedwordcounter.update(data = {
                    'count': res.count + 1
                }, where={
                    'userId': userId
                })
            else:
                client.blacklistedwordcounter.create(data = {
                    'userId': userId,
                    'count': 1
                })
            await client.disconnect()
            return True
    return False
