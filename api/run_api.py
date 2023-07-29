import pathlib

import uvicorn
from config import HOST, PORT, WORKERS


if __name__ == "__main__":
    cwd = pathlib.Path(__file__).parent.resolve()
    uvicorn.run(
        "api.app:app",
        host=HOST,
        log_level="info",
        port=PORT,
        # reload=True,
        workers=WORKERS
    )
