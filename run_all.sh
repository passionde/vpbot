
source venv/bin/activate
pm2 start run_bot.py --interpreter=python3
pm2 start run_api.py --interpreter=python3
pm2 start run_scheduler.py --interpreter=python3