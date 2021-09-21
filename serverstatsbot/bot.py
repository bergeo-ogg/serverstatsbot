import asyncio
import logging
import os
import requests
from datetime import datetime

from .utils import load_json, write_json
from .constants import *

rootLogger = logging.getLogger(__name__)
rootLogger.setLevel(logging.DEBUG)


class StatsBot:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def run(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        request_member_splits = self.get_member_count_splits()
        discoverable_guilds = await self.collect_discoverable_guilds(
            request_member_splits
        )

        rootLogger.info(
            f"Collected {len(discoverable_guilds)} discoverable guilds! Outting to file..."
        )
        write_json(f"guild_list.json", discoverable_guilds)
        rootLogger.info('See "guild_list.json" for data!')

    def get_member_count_splits(self):
        json_files = [
            pos_json
            for pos_json in os.listdir("discovery_dumps")
            if pos_json.endswith(".json")
        ]
        member_counts = []
        if len(json_files) == 0:
            member_counts = FIRST_RUN_GUILD_NUMBERS
        else:
            member_counts.append(0)
            dump = load_json(f"discovery_dumps/{max(json_files)}")
            raw_member_counts = self.get_member_counts(dump)
            for i in range(1, len(raw_member_counts) // MEMBER_STEP + 1):
                member_counts.append(raw_member_counts[i * MEMBER_STEP])
            member_counts.append(10000000)  # > Max guild member count
        return member_counts

    def get_member_counts(self, dump: dict):
        approximate_member_counts = []
        for guild in list(dump.values()):
            approximate_member_counts.append(guild["approximate_member_count"])
        approximate_member_counts = sorted(approximate_member_counts)
        return approximate_member_counts

    async def collect_discoverable_guilds(self, splits):
        guild_dict = dict()
        for i in range(0, len(splits) - 1):
            await asyncio.sleep(0.5)
            guild_chunk = await self.get_guild_chunk(splits[i], splits[i + 1])
            if guild_chunk["nbHits"] > 1000:
                rootLogger.warning("Section failed. Falling back on first run numbers.")
                guild_dict = dict()
                for j in range(0, len(FIRST_RUN_GUILD_NUMBERS) - 1):
                    guild_chunk = await self.get_guild_chunk(
                        FIRST_RUN_GUILD_NUMBERS[j], FIRST_RUN_GUILD_NUMBERS[j + 1]
                    )
                    if guild_chunk["nbHits"] > 1000:
                        rootLogger.error(
                            "First run numbers had section of more than 1k. Please update the first run numbers."
                        )
                        os._exit(1)
                    temp_dict = {guild["id"]: guild for guild in guild_chunk["hits"]}
                    guild_dict.update(temp_dict)
                break
            else:
                temp_dict = {guild["id"]: guild for guild in guild_chunk["hits"]}
                guild_dict.update(temp_dict)
        return guild_dict

    async def get_guild_chunk(self, min: int, max: int):
        try:
            rootLogger.info(f"Collecting guilds between {min} and {max} members.")
            body = {
                "filters": f"approximate_member_count >= {min} AND approximate_member_count < {max}",
                "hitsPerPage": 1000,
            }
            str_body = str(body).replace("'", '"')
            r = requests.post(API_ENDPOINT, headers=API_HEADERS, data=str_body)
        except Exception as e:
            rootLogger.error(e)
            os._exit(1)
        return r.json()


if __name__ == "__main__":
    bot = StatsBot()
    bot.run()
