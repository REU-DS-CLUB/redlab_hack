import wandb
import json

with open('config.json', 'r') as file:
    config = json.load(file)

def init_exp(exp_tags=[]):
    if config['logging']:
        with open('wandb_secret.txt', 'r') as file:
            api_key = file.read()
        wandb.login(key=api_key)
        wandb.init(project="redlab-hack", tags=exp_tags)


def log_params(params={}):
    if config['logging']:
        wandb.log(params)
        wandb.finish()