#!/usr/bin/env python
"""Check accessing the default client from an atexit hook."""
import atexit

# Intentionally named with a hyphen to ensure this can't be imported

import lmstudio as lms

# TODO: Turn this into a CI test case (perhaps via subprocess invocation?)

# Prior to lmstudio-python 1.5.0, the atexit hook below would hang on shutdown.
# By the time atexit hooks run, asyncio.to_thread no longer works due to all
# concurrent.futures managed thread pools (including those used by asyncio)
# being shut down before the interpreter waits for non-daemon threads to terminate.
# Since the synchronous client relied on asyncio.to_thread to deliver
# messages from the async background comms thread to the blocking
# foreground thread, the sync API didn't work in this scenario.
# In 1.5.0, the sync message reception was reworked to queue messages entirely
# in the async background thread with blocking async queue reads, eliminating
# the blocking queue write options, and allowing the client to continue running
# in atexit threads
def access_default_client(client: lms.Client):
    """Ensure default client can be accessed from an atexit hook."""
    print("During shutdown:", end=" ", flush=True)
    print(client.list_loaded_models())

atexit.register(access_default_client, lms.get_default_client())

print("Prior to shutdown:", lms.list_loaded_models())
