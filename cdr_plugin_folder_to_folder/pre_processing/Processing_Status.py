
class Processing_Status:
    NONE     = "None"
    STOPPED  = "Stopped"
    STOPPING = "Stopping"
    STARTED  = "Started"
    PHASE_1  = "PHASE 1 - Copying Files"
    PHASE_2  = "PHASE 2 - Rebuilding Files"

Processing_Status_States  = [   Processing_Status.NONE, 
                                Processing_Status.STOPPED,
                                Processing_Status.STOPPING,
                                Processing_Status.STARTED,
                                Processing_Status.PHASE_1,
                                Processing_Status.PHASE_2]