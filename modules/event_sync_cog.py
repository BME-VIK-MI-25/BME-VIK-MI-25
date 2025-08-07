from disnake.ext import commands
import disnake 
import requests
from dotenv import load_dotenv
import os
import datetime
from bs4 import BeautifulSoup

load_dotenv()

class EventSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#description="Synchronize Discord events with the BME events!"
    @commands.slash_command()
    async def eventsync(self, inter):
        
        bme_events_url = os.getenv("BME_EVENTS_URL")
        await inter.response.send_message("szia")
        bme_events_raw = requests.get(bme_events_url)
        bme_events_html = bme_events_raw.json()
        bme_events_html= bme_events_html[2]["data"]
        
        soup = BeautifulSoup(bme_events_html, 'html.parser')
        
        time_elements = [soup.find_all(class_="bme_event_card-date")]
        for el in time_elements:
            print(el)
            if el.__contains__("-"):
                print("end date included")

        return
    
def setup(bot):
    bot.add_cog(EventSync(bot))