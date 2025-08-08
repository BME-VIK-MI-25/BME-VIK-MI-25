import logging, os

LOGDIR = "logs"
LOGFILE = "bot.log"

os.makedirs(LOGDIR, exist_ok=True)

def LogSetup():
    logging.basicConfig(
        level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=f'{LOGDIR}/{LOGFILE}',
        filemode="a",
        encoding='utf-8'
    )

LogSetup()

"""
Ezek vannak:
logging.debug("Ez egy debug üzenet (fejlesztéshez)")
logging.info("Ez egy info üzenet")
logging.warning("Ez egy figyelmeztetés")
logging.error("Ez egy hiba")
logging.critical("Ez egy kritikus hiba")
"""