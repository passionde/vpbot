
source venv/bin/activate
sudo systemctl start run_bot.service
sudo systemctl start run_api.service
sudo systemctl start run_scheduler.service

sudo systemctl status run_bot.service
sudo systemctl status run_api.service
sudo systemctl status run_scheduler.service

sudo systemctl restart run_bot.service
sudo systemctl restart run_api.service
sudo systemctl restart run_scheduler.service