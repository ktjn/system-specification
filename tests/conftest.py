from build_support import sync_all

# Run at import time (not inside a fixture): test modules import system_spec_ref.* at
# collection time, before any fixture would execute.
sync_all()
