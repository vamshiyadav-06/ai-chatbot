import sys
import asyncio

# Patch asyncio to avoid RuntimeError in Python 3.14+
if sys.version_info >= (3, 14):
    _original_get_event_loop = asyncio.get_event_loop
    def _patched_get_event_loop():
        try:
            return _original_get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    asyncio.get_event_loop = _patched_get_event_loop

import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())
