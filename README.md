# serverstatsbot
Pulls discoverable guilds via the algolia API, instead of using selfbotting of /discoverable-guilds. This returns approximately two times the guilds compared to /discoverable-guilds with the following limitations:
* Partial lists of emoji and stickers are not returned.
* Features are filtered to features useful for the listing, or immediately on join.
* Applications associated with the guild are not returned.
