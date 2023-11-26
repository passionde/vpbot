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
        workers=WORKERS,
        log_config=f"{cwd}/log.ini",
        ssl_certfile="/etc/letsencrypt/live/vpchallenge.tw1.su/fullchain.pem",
        ssl_keyfile="/etc/letsencrypt/live/vpchallenge.tw1.su/privkey.pem",
    )
