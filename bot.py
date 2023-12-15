import discord
import mysql.connector
import os

# Database connection details
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="discord_bots"
)

mycursor = mydb.cursor()

# Create a table to store server information if it doesn't exist
mycursor.execute("CREATE TABLE IF NOT EXISTS discord_servers (server_id VARCHAR(255) PRIMARY KEY, server_name VARCHAR(255))")

# Define a function to fetch server name from database
def get_server_name_from_db(server_id):
    mycursor.execute("SELECT server_name FROM discord_servers WHERE server_id = %s", (server_id,))
    result = mycursor.fetchone()
    if result:
        return result[0]
    else:
        # Handle case where server isn't found in database
        print(f"Server ID {server_id} not found in database.")
        return None

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_guild_join(self, guild):
        server_id = guild.id
        server_name = guild.name

        mycursor.execute("INSERT INTO discord_servers (server_id, server_name) VALUES (%s, %s)", (server_id, server_name))
        mydb.commit()

        print(f"Joined server: {server_name} (ID: {server_id})")

    async def on_message(self, message):
        if message.content.startswith("!hello"):
            server_id = message.guild.id
            server_name = get_server_name_from_db(server_id)

            if server_name:
                await message.channel.send(f"Hello World! in {server_name}")
            else:
                await message.channel.send(f"Couldn't find the server name for ID: {server_id}")

client = MyClient(intents=discord.Intents.default())
bot_token = os.environ["BOT_TOKEN"]


client.run(bot_token)
