from telethon import TelegramClient, events, utils
from telethon.tl.types import InputBotInlineResult
from datetime import datetime
import logging, argparse, os, subprocess


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',level=logging.WARNING)

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--TOKEN', required=True)
parser.add_argument('-i', '--api_id', type=int, required=True)
parser.add_argument('-q', '--api_hash', required=True)
args = parser.parse_args()

TOKEN = args.TOKEN
api_id = args.api_id
api_hash = args.api_hash

bot = TelegramClient('pythoncompiler', api_id, api_hash).start(bot_token=TOKEN)


@bot.on(events.NewMessage)
async def start(event):
    chat = await event.get_sender()
    async with bot.conversation(chat) as conv:
        await conv.send_message('Python 3.7.4 ({} {})\n >>> send code here'.format(chat.username, str(datetime.now())))
        code = await conv.get_response()
        if code.text:
            name = str(chat.id)+'.py'
            with open(name, 'w') as main:
                main.write("import builtins, os, sys\n")
                main.write("del os\n")
                main.write("sys.modules['os']=None\n")
                main.write("builtins.open = lambda x, y: print('NameError: name open is not defined')\n")
                main.write(code.text + '\n')

            command = subprocess.Popen(['python', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, error = command.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                command.kill()
                output, error = command.communicate()

            if error:
                if 'os' in error.decode('utf-8'):
                    await conv.send_message('>>>\n{}'.format("\U0001F610"))
                else:
                    await conv.send_message('>>>\n{}'.format(error.decode('utf-8')))
            else:
                await conv.send_message('>>>\n{}'.format(output.decode('utf-8')))



@bot.on(events.InlineQuery)
async def inlinehandler(event):
    builder = event.builder
    chat = await event.get_sender()
    name = str(chat.id)+'.py'
        
    with open(name, 'w') as main:
        main.write("import builtins, os, sys\n")
        main.write("del os\n")
        main.write("sys.modules['os']=None\n")
        main.write("builtins.open = lambda x, y: print('NameError: name open is not defined')\n")
        main.write(event.text + '\n')
        
    command = subprocess.Popen(['python', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, error) = command.communicate()

 
    if error:
        if 'os' in error.decode('utf-8'):
            await event.answer([builder.article('see output', text='>>>\n{}'.format("\U0001F610"))])
        else:
            await event.answer([builder.article('see output', text='>>>\n{}'.format(error.decode('utf-8')))])
    else:
        await event.answer([builder.article('see output', text='>>>\n{}'.format(output.decode('utf-8')))])


        
bot.run_until_disconnected()


