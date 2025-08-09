from disnake.ext import commands, tasks
import disnake 
from disnake import GuildScheduledEventMetadata
import requests
from dotenv import load_dotenv
import os
import datetime
from bs4 import BeautifulSoup
from modules.variables import BME_EVENTS_CHANNEL_ID, GENERAL_CHANNEL_ID, GUILD_ID

load_dotenv()

class Event():
    def __init__(self, name, description, location, start_date, end_date):
        self.name = name
        self.description = description
        self.location = location
        self.start_date = start_date
        self.end_date = end_date


def GetDateFromText(text: str):
    split = text.split(' - ')
    time = split[1]
    hours = int(time.split(':')[0])
    minutes = int(time.split(':')[1])
    date = split[0]
    date_split = date.split('. ')
    year = int(date_split[0].replace(".", ""))
    month = int(date_split[1].replace(".", ""))
    day = int(date_split[2].replace(".", ""))

    date = datetime.datetime(year, month, day, hours, minutes)
    return date

class EventSync(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.guild = self.bot.get_guild(GUILD_ID)
        self.event_checker.start()

#description="Synchronize Discord events with the BME events!"
    @commands.slash_command(description="Synchronize the Discord events with the BME events!")
    @commands.has_permissions(administrator=True)
    async def eventsync(self, inter: disnake.ApplicationCommandInteraction):
        
        await inter.response.send_message("A szinkronizálás megkezdődött..")

        bme_events_url_page_1 = os.getenv("BME_EVENTS_URL_PAGE_1")
        bme_events_raw_page_1 = requests.get(bme_events_url_page_1)
        bme_events_html_page_1 = bme_events_raw_page_1.json()
        bme_events_html_page_1 = bme_events_html_page_1[2]["data"]
        
        soup_1 = BeautifulSoup(bme_events_html_page_1, 'html.parser')
        event_elements_1 = soup_1.find_all(class_="views-view-responsive-grid__item")
        bme_events_url_page_2 = os.getenv("BME_EVENTS_URL_PAGE_2")
        bme_events_raw_page_2 = requests.get(bme_events_url_page_2)
        bme_events_html_page_2 = bme_events_raw_page_2.json()
        bme_events_html_page_2 = bme_events_html_page_2[2]["data"]
        
        soup_2 = BeautifulSoup(bme_events_html_page_2, 'html.parser')
        event_elements_2 = soup_2.find_all(class_="views-view-responsive-grid__item")

        events = []
        all_event_elements = event_elements_1 + event_elements_2
        for el in all_event_elements:
            str_el = str(el)
            this_soup = BeautifulSoup(str_el, 'html.parser')

            time_element = this_soup.find(class_="bme_event_card-date")
            this_soup = BeautifulSoup(str(time_element), 'html.parser')

            start_date_text = this_soup.find(class_="nowrap").get_text()
            end_date_text = None

            if len(this_soup.find_all(class_="nowrap")) >= 2:
                end_date_text = this_soup.find_all(class_="nowrap")[1].get_text()
            else:
                end_date_text = start_date_text

            start_date = None
            end_date = None

            start_date_text = start_date_text.replace("\n", "")
            end_date_text = end_date_text.replace("\n", "")

            start_date = GetDateFromText(start_date_text)

            if start_date_text == end_date_text:
                end_date = start_date
                end_date += datetime.timedelta(hours=1)
            else:
                end_date = GetDateFromText(end_date_text)

            title_element = el.find(class_="bme_event_card-title")
            title = title_element.get_text().replace("\t", "").replace("\n", "").strip()
            location_element = el.find(class_="bme_event_card-location")
            location = location_element.get_text()
            body_element = el.find(class_="bme_event_card-body")
            body = body_element.get_text()

            events.append(Event(title, body, location, start_date, end_date))

        scheduled_events = await inter.guild.fetch_scheduled_events()
        event_names = []

        for event in events:
            event_names.append([event.name, event.start_date])

        for event in scheduled_events:
            for e_name in event_names:
                if e_name[0] == event.name:
                    event_names.remove(e_name)
                    break

        for event in events:
            if [event.name, event.start_date] in event_names:
                metadata = GuildScheduledEventMetadata(location=event.location)
                scheduled_event = await inter.guild.create_scheduled_event(name=event.name, entity_type=disnake.GuildScheduledEventEntityType.external, description=event.description, scheduled_end_time=event.end_date, scheduled_start_time=event.start_date, privacy_level=disnake.GuildScheduledEventPrivacyLevel.guild_only, entity_metadata=metadata)
                await inter.guild.get_channel(BME_EVENTS_CHANNEL_ID).send(f"[{event.name}]({scheduled_event.url})")
        await inter.channel.send("A szinkronizálás befejeződött!")
    
    @tasks.loop(minutes=3)
    async def event_checker(self):
        events = await self.guild.fetch_scheduled_events()
        for event in events:
            description = event.description or ""
            if "1 NAP VAN HÁTRA!" in description:
                continue
            
            start = event.scheduled_start_time
            current_datetime = datetime.datetime.now(datetime.timezone.utc)
            difference = start - current_datetime
            minutes_left = difference.total_seconds() / 60
            day_in_minutes = 24 * 60

            if minutes_left < day_in_minutes:
                event_url = event.url
                await self.guild.get_channel(GENERAL_CHANNEL_ID).send(
                    f"A következő [esemény]({event_url})ig kevesebb mint 1 nap van hátra"
                )
                new_description = description + "\n1 NAP VAN HÁTRA!"
                await event.edit(description=new_description)
    
def setup(bot):
    bot.add_cog(EventSync(bot))