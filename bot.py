import discord
import mysql.connector
import os

# Database connection details (modify based on your configuration)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="discord_bots"
)

# Create a cursor
mycursor = mydb.cursor()

# Create a table to store server information if it doesn't exist (modify column names if needed)
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

# Define the Discord bot client
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    # Store server information upon joining a new server
    async def on_guild_join(self, guild):
        server_id = guild.id
        server_name = guild.name

        mycursor.execute("INSERT INTO discord_servers (server_id, server_name) VALUES (%s, %s)", (server_id, server_name))
        mydb.commit()

        print(f"Joined server: {server_name} (ID: {server_id})")

    # Update server name if changed (optional)
    async def on_guild_update(self, before, after):
        if before.name != after.name:
            server_id = after.id
            server_name = after.name

            mycursor.execute("UPDATE discord_servers SET server_name = %s WHERE server_id = %s", (server_name, server_id))
            mydb.commit()

            print(f"Server name updated for server: {server_name} (ID: {server_id})")

    # Handle messages and commands
    async def on_message(self, message):
        # Example command logic with database server name
        if message.content.startswith("!hello"):
            server_id = message.guild.id
            print(server_id)
            server_name = get_server_name_from_db(server_id)
            print(server_name)

            # Use the server_name from the database
            if server_name:
                await message.channel.send(f"Hello World! in {server_name}")
            else:
                # Handle case where server name couldn't be retrieved
                await message.channel.send(f"Couldn't find the server name for ID: {server_id}")

# Create and run the bot with required intents
client = MyClient(intents=discord.Intents.default())
# client.run("YOUR_DISCORD_BOT_TOKEN")
bot_token = os.environ["BOT_TOKEN"]


client.run(bot_token)
