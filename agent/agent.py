# agent.py

import asyncio
import yaml
from core.loop import AgentLoop
from core.session import MultiMCP
import warnings
import os
from channels.telegram import TelegramChannel
from channels.manager import ChannelManager
from channels.chrome import ChromeChannel

from config.log_config import setup_logging

logger = setup_logging(__name__)

warnings.filterwarnings("ignore", category=ResourceWarning)

def log(stage: str, msg: str):
    """Simple timestamped console logger."""
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")


async def main():
    print("🧠 Cortex-R Agent getting ready...")

    # Load config
    with open("config/profiles.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers = profile.get("mcp_servers", [])
        interaction_channel = profile.get("interaction_channel", "telegram").lower()
        channel_config = next(
            (ch for ch in profile.get("channels", []) if ch["type"] == interaction_channel), None
        )

    ready_flag = asyncio.Event()

    # Initialize MCP
    multi_mcp = MultiMCP(server_configs=mcp_servers)
    await multi_mcp.initialize()

    # Initialize the selected channel
    if interaction_channel == "telegram":
        channel = TelegramChannel(multi_mcp, ready_flag)
    elif interaction_channel == "chrome":
        channel = ChromeChannel(url=channel_config.get("url", "http://localhost:5000"), ready_flag=ready_flag)
    else:
        raise ValueError(f"Unknown interaction_channel: {interaction_channel}")

    channel_manager = ChannelManager([channel])
    await channel_manager.start()
    ready_flag.set()
    print(f"🧠 Cortex-R Agent is now ready and listening on: {interaction_channel}")

    while True:
        user_id, user_input = await channel_manager.get_query()
        if user_input.strip().lower() in {"exit", "quit", ""}:
            print("👋 Goodbye!")
            break

        agent = AgentLoop(
            user_input=user_input,
            dispatcher=multi_mcp
        )

        try:
            final_response = await agent.run()
            await channel_manager.send_response(final_response.replace("FINAL_ANSWER:", "").strip(), user_id)
        except Exception as e:
            log("fatal", f"Agent failed: {e}")
            raise

    await channel_manager.stop()
    await multi_mcp.shutdown()



if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(asyncio.sleep(0.1))  # Give time for cleanup
        loop.close()

# Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.
# How much Anmol singh paid for his DLF apartment via Capbridge? (This uses RAG)
# What is the log value of the amount that Anmol singh paid for his DLF apartment via Capbridge? (This runs the log funtion via python code)
# Summarize this page: https://theschoolof.ai/ (This uses search and summarize)
# What is this document all about? Can you summarize it for me? "C:\Users\dsaha\OneDrive - Microsoft\Documents\Personal\deep\study\artificial intelligence\eagv1\eag8\sample\How to use Canvas LMS.pdf" (This uses PDF)
# What do you know about Don Tapscott and Anthony Williams?
# What is the relationship between Gensol and Go-Auto?
# which course are we teaching on Canvas LMS?
# Find the current point standings of F1 Racers from the internet, and update the results into a spreadsheet in Google Drive, and then share the link to this spreadsheet with me on deepjyoti.saha@gmail.com. While wriiing the result into the spreadsheet, first check if a spreadsheet already exists in Google Drive, with a similar name, if yes, then update the results in the existing spreadsheet with the new results, make sure to update the exact cells; else if no spreadsheet exists, then create a new spreadsheet and update the results; Your email should be well formatted in HTML format.

#- ✅ When searching rely on first reponse from tools, as that is the best response probably. However, ALWAYS check if the response is already available in memory via a previous tool call with same parameters, as that is the most efficient use of time and resources.

#Find the current point standings of F1 Racers from the internet and update the results into a spreadsheet in Google Drive, and then share the link to this spreadsheet with me on deepjyoti.saha@gmail.com. Update the final answer with the text only message in Telegram.


