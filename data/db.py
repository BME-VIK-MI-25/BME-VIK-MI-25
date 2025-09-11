VerificationDict = {} # email -> str: authcode -> int

InviteDict = {} # inviteeid -> int: inviterid -> int

moderationDict = {} # userID -> int: [bannedCount -> int, inviteBanExpiry -> datetime]

with open('data/banned_words.txt', 'r') as f:
    banned_words = [line.strip() for line in f] # list of banned words