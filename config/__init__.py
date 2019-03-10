import os

execution_environment = os.getenv("EXEC", "prod")
if execution_environment == "dev":
    from .dev import *
elif execution_environment == "prod":
    from .prod import * 
