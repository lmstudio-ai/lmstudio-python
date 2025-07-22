#!/usr/bin/env python
"""Open a client instance for link failure testing."""
import asyncio
import logging
import sys
import time

from lmstudio import AsyncClient, Client

LINK_POLLING_INTERVAL = 1

async def open_client_async():
    """Start async client, wait for link failure."""
    print("Connecting async client...")
    async with AsyncClient() as client:
        await client.list_downloaded_models()
        print ("Async client connected. Close LM Studio to terminate.")
        while True:
            await asyncio.sleep(LINK_POLLING_INTERVAL)
            await client.list_downloaded_models()

def open_client_sync():
    """Start sync client, wait for link failure."""
    print("Connecting sync client...")
    with Client() as client:
        client.list_downloaded_models()
        print ("Sync client connected. Close LM Studio to terminate.")
        while True:
            time.sleep(LINK_POLLING_INTERVAL)
            client.list_downloaded_models()

if __name__ == "__main__":
    # Link polling makes debug logging excessively spammy
    log_level = logging.DEBUG if "--debug" in sys.argv else logging.INFO
    logging.basicConfig(level=log_level)
    if "--async" in sys.argv:
        asyncio.run(open_client_async())
    else:
        open_client_sync()
