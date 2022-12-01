import gc
import cms

gc.freeze()
gc.disable()
cms.run_app(port=8000)
