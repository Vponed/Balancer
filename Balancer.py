# -- coding: <utf-8>
import psutil
import time
import subprocess
import concurrent.futures
from datetime import datetime
from telethon import TelegramClient, events,utils,types
import plyer
from audioplayer import AudioPlayer
import json
import asyncio

interval = 60
api_id = 995882
api_hash = 'e16a408ef4d8f0dccc608edfa67968c8'


def logging(text):
	file = open('balancer.log', "a+")
	file.write(str(datetime.now()) + " " + text + '\n')  # \n добавляет перенос строки
	file.close()
	#print(text)
	pass


def telegram_watching():
	my_channel_id = 't.me/message_alerter'
	file =  open("telegram.json", "r")
	json_data = json.load(file)
	file.close()
	client = TelegramClient('Message_Watcher', api_id, api_hash)
	# if not "t.me" in parsed_list[0]:
	# 	parsed_list[0] = utils.get_peer_id(types.PeerChannel(int(parsed_list[0])))
	# 	print(parsed_list[0],"   ",users)
		
	@client.on(events.NewMessage())
	async def my_event_handler(event):
		# if (event.get_chat.id in json_data['chats']):
		# 		print(event.get_chat.id)
		if event.message:
			#print(event.message.peer_id.channel_id)
			try:
				if str(event.message.peer_id.channel_id) in json_data ['chats']:
					#print(event.message.peer_id.channel_id)
					#print(json_data ['chats'])
					pass
			except AttributeError:
				return
				#print(event.message)
				#message = event.message.text, "\n", event.message.id
				#print(message)
				#await client.forward_messages(my_channel_id, event.message,event.message.peer_id)
				#AudioPlayer(mp3_file).play(block=True)
				#message_str = "Важное обновление телеграм " + str(event.message.from_id) + event.message.message
				#plyer.notification.notify(message=message_str, app_name='Telegram alerter', title='Ахтунг')
		
		# channel_ID, user_ID_list, white_word_list, black_word_list = parsed_list[0], parsed_list[1], parsed_list[2], parsed_list[3]
		#users = []
				
#	client.start()
#	client.run_until_disconnected()

def net_activity():
	t0 = time.time()
	upload0 = psutil.net_io_counters().bytes_sent
	download0 = psutil.net_io_counters().bytes_recv
	time.sleep(interval)
	
	t1 = time.time()
	upload1 = psutil.net_io_counters().bytes_sent
	download1 = psutil.net_io_counters().bytes_recv
	
	upload = (upload1 - upload0) / (t1 - t0)
	download = (download1 - download0) / (t1 - t0)
	ret1 = round(upload / 1000000, 3)
	ret2 = round(download / 1000000, 3)
	return ret1, ret2


def hard_work(interval):
	psutil.cpu_percent()
	time.sleep(interval)
	cpu_free = psutil.cpu_percent()
	memory_free = psutil.virtual_memory().free
	return cpu_free, memory_free
	pass


def killer(command_kill):
	p = subprocess.Popen(command_kill, shell=False)#, stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
	p.wait()
	if p.returncode != 0:
		logging("Error killing")
		pass
	else:
		logging(command_kill + " Success")
	pass


cycle_index = 0
flag_execution = False
flag_except_prog = False
#telegram_watching()
# with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
# 	telegram = executor.submit(telegram_watching())

#while True:
#	telegram_watching(1)
#	time.sleep(1)

while True:
	#    print(cycle_index)
	cycle_index += 1
	#print(cycle_index)
	file = open('balancer.ini', "r", encoding='utf-8')
	list_with_file_content = file.read().splitlines()
	file.close()
	with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
		future = executor.submit(net_activity) #, interval)  #
		upload, download = future.result()
	
	with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
		future = executor.submit(hard_work, interval)
		cpu_free, memory_free = future.result()
	
	# print(upload,download,cpu_free,memory_free)
	list_with_file_content.pop(0)  # режем первую строчку
	for foreach_data in list_with_file_content:
		parsed_list = foreach_data.split("+++++", 8)
		path_to_file, exec_file, max_cpu, max_ram, max_upload, max_download, command_kill, except_prog = parsed_list[
			                                                                                                 0], \
		                                                                                                 parsed_list[
			                                                                                                 1], \
		                                                                                                 parsed_list[
			                                                                                                 2], float(
			parsed_list[3]) * 1024000, parsed_list[4], parsed_list[5], parsed_list[6], parsed_list[7]
		except_list = except_prog.split(',')
		for proc in psutil.process_iter():
			name = proc.name()
			if name == exec_file and flag_execution == False:
				flag_execution = True
				logging('Найдена отслеживаемая программа:' + name)
				pass
			if name in except_list and flag_except_prog == False:
				flag_except_prog = True
				logging('Найдена программа-исключение: ' + name)
				pass
			# if flag_except_prog == True and flag_execution == True:
			#    break
		pass
		
		if command_kill != '0':
			command_kill_fin = command_kill
			pass
		else:
			command_kill_fin = 'taskkill /f /t /im ' + exec_file
			pass
		
		if flag_execution == True:  # решаем убивать ли процесс
			
			if cpu_free > float(max_cpu):
				logging('Превышена загрузка cpu. Убиваем целевую программу:' + str(cpu_free))
				killer(command_kill_fin)
				continue
			if memory_free < int(max_ram):
				logging('Превышена загрузка памяти. Убиваем целевую программу:' + str(memory_free))
				killer(command_kill_fin)
				continue
			if upload > float(max_upload) and max_upload != '0':
				logging('Превышена загрузка сети upload. Убиваем целевую программу::' + str(upload))
				killer(command_kill_fin)
				continue
			if download > float(max_download) and max_download != '0':
				logging('Превышена загрузка сети download. Убиваем целевую программу:' + str(download))
				killer(command_kill_fin)
				continue
			if flag_except_prog:
				logging('Запущена программа-исключение. Убиваем целевую программу:')
				killer(command_kill_fin)
				continue
			pass
		else:
			if (cpu_free < float(max_cpu) and max_cpu != '0'):
				logging('Загрузка cpu=' + str(cpu_free) + '<' + max_cpu)
				if (memory_free > max_ram):
					logging('Свободная память:mem=' + str(memory_free) + '>' + str(max_ram))
					if (upload < float(max_upload)) or max_upload == '0':
						logging('Upload (Mbps): ' + str(upload) + '<' + max_upload)
						if (download < float(max_download)) or max_download == '0':
							logging('Download (Mbps): ' + str(download) + '<' + max_download)
							if (flag_except_prog == False):
								logging("Запущена ли программа-исключение:" + str(flag_except_prog))
								logging('Все параметры в норме. Запускаем:' + exec_file)
								# , creationflags=subprocess.CREATE_BREAKAWAY_FROM_JOB
								success_var = subprocess.Popen(path_to_file + exec_file)
								logging("Успешно")
								pass
							pass
						pass
					pass
				pass
			pass
		
		pass
	flag_execution = False
	flag_except_prog = False
	time.sleep(60)
	pass
