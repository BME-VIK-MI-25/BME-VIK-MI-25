from prisma import Client
import random
async def CreateAuthCode(email: str):
    client = Client()
    await client.connect()
    authCode = random.randint(1000000000, 9999999999)
    await client.auth.create(
        data = {
            'email': email,
            'authcode': authCode
        }
    )
    await client.disconnect()
    return authCode

async def CheckAuthCode(authCode: str):
    client = Client()
    await client.connect()
    authCode = int(authCode)
    result = await client.auth.find_first(
        where={
            'authcode': authCode
        }
    )
    if result == None:
        return False
    else:
        await RemoveAuthCode(authCode)
        return True

async def RemoveAuthCode(authCode: str):
    client = Client()
    authCode = int(authCode)
    await client.connect()
    await client.auth.delete(
        where={
            'authcode': authCode
        }
    )
    await client.disconnect()

async def InsertInviteData(inviteeId: int, inviterId: int):
    client = Client()
    await client.connect()
    await client.invite.create(
        data={
            'inviteeid': inviteeId,
            'inviterId': inviterId
        }
    )
    await client.disconnect()
    
async def RemoveInviteData(inviteeId: int, inviterId: int):
    client = Client()
    await client.connect()
    await client.invite.delete(
        where={
            'inviteeid': inviteeId,
            'inviterId': inviterId
        }
    )
    await client.disconnect()