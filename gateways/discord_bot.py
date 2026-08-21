import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

class MLXDiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.gemini_engine import GeminiAEAgent
        print("🧠 [Discord Bot] Initializing High-Intelligence Google Gemini Engine...")
        self.agent = GeminiAEAgent()
        print("✅ [Discord Bot] Google Gemini Brain is LIVE (Cloud Native, 0GB Local Disk)!")

    async def on_ready(self):
        print(f"[Discord Bot] Logged in as {self.user} (ID: {self.user.id})")
        print("[Discord Bot] Ready to receive commands from Discord channels!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        print(f"[Discord Bot] Received message: '{message.content}' from {message.author} (Attachments: {len(message.attachments)})")
        async with message.channel.typing():
            try:
                full_prompt = message.content or ""

                # Download and read text file attachments
                if message.attachments:
                    for attachment in message.attachments:
                        if any(attachment.filename.lower().endswith(ext) for ext in [".txt", ".md", ".csv", ".json", ".py", ".log", ".yaml", ".yml"]):
                            file_bytes = await attachment.read()
                            file_text = file_bytes.decode("utf-8", errors="ignore")
                            full_prompt += f"\n\n[첨부파일: {attachment.filename}]\n{file_text[:8000]}"

                # Non-blocking async thread execution with per-channel conversation memory
                session_id = str(message.channel.id)
                response = await asyncio.to_thread(self.agent.chat, full_prompt, session_id)
                
                if not response or not response.strip():
                    response = "답변 생성 실패 (응답이 비어있음)"

                if len(response) > 2000:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
            except Exception as e:
                err_msg = f"[ERROR] MLX Engine Failure: {e}"
                print(err_msg)
                await message.channel.send(err_msg)

def start_discord_bot():
    token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        print("[ERROR] DISCORD_BOT_TOKEN is missing in mlx_agent/.env!")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    
    client = MLXDiscordClient(intents=intents)
    client.run(token)
