import random

async def CreateAuthCode(email: str, authDict: dict) -> None:
    authCode = random.randint(1000000000, 9999999999)
    authDict.update({email: authCode})

async def CheckAuthCode(authCode: str, authDict: dict) -> bool:
    authCode = int(authCode)

    if authCode not in authDict.values():
        return False
    else:
        for key, value in authDict.items():
            if value == authCode:
                authDict.pop(key)
                return True

async def InsertInviteData(inviteeId: int, inviterId: int, inviteDict: dict) -> None:
    inviteDict.update({inviteeId: inviterId})
    
async def GetInviteData(inviteeId: int, inviteDict: dict) -> int | None:
    
    InviterID = inviteDict.get(inviteeId)
    if InviterID is None:
        return None
    else:
        return InviterID

async def RemoveInviteData(inviteeId: int, inviteDict: dict) -> None:
    inviteDict.pop(inviteeId, None)