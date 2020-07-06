TELEGRAM_TOKEN = '1128593176:AAHmtlbFTWcXIu-s2InMW0uvF7GnsYjtVoE'
VK_TOKEN = 'a726f4bd341c310822a99d83a1b2e6664b39cd6146508791dcc964a4d5b6e6387a57f7161a1463e2fd0cf'

prx = '91.188.230.167:60873:suxh1oYYPS:JKAYsLFRo8'
prx = prx.split(':')
PROXY = {'proxy_url': f'socks5://{prx[0]}:{prx[1]}',
         'urllib3_proxy_kwargs': {'username': prx[2], 'password': prx[3]}}