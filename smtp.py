from verify import CreateAuthCode

def CodePreviouslySent(email: str):
    if True: # STUB, check for: EMAIL - CODE pair in DB!
        return True
    return False

def SendAuthCode(email: str):
    if CodePreviouslySent():
        # Handle previously code
        return
    auth_code = CreateAuthCode()
    return