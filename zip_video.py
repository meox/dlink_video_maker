#!/usr/bin/python

import sys

from os import walk, path, makedirs
from datetime import datetime
from shutil import copyfile, rmtree
import subprocess


prefix 			= "DCS-932LB"
output_video 	= "/mnt/disk-master/video/"



def main(rpath_in):
	time_board = {}
	video_index = 0
	for (dirpath, dirnames, filenames) in walk(rpath_in):
		for fname in filenames:
			ext = fname[fname.rfind('.')+1:]
			
			#DCS-932LB2016071622390105.jpg
			if ext != "jpg":
				continue
			
			start_prefix = fname.find(prefix)
			if start_prefix == -1:
				continue
			
			# extract date
			start_date = start_prefix + len(prefix)
			fdate = fname[start_date : start_date + 8]

			start_time = start_date + 8
			ftime = fname[start_time : start_time + 6]

			p = int(fname[start_time+6:fname.rfind('.')])

			date_object = datetime.strptime(fdate, '%Y%m%d')
			date_object = date_object.replace(hour=int(ftime[0:2]), minute=int(ftime[2:4]), second=int(ftime[4:6]), microsecond=1000*p)

			#print("%s - %s (prog: %d)" % (fdate, ftime, p))
			time_board[date_object] = (dirpath, fname)


	img_index = 0
	start_frame = 0
	tindex = 0
	current = []

	for k in sorted(time_board):
		if tindex == 0:
			start_frame = k

		if tindex == 0 or (k - tindex).total_seconds() <= 30:
			tindex = k
			#print(k, time_board[k])
			current.append((img_index, time_board[k]))
			img_index = img_index + 1
		else:
			make_video(video_index, current, start_frame)
			video_index = video_index + 1

			current = []
			tindex = 0
			img_index = 0

		#print ("t: %s, fname: %s" % (k, time_board[k]))
	if len(current) > 0:
		make_video(video_index, current, start_frame)


def make_video(video_index, list_frames, tindex):
	#avconv -r 10 -i filename_%d.jpg -b:v 1000k test.mp4

	if len(list_frames) == 0:
		return

	video_tmp = "/tmp/video/"
	video_name = "tele%d_%s.mp4" % (video_index, str(tindex))

	if not path.exists(video_tmp):
		makedirs(video_tmp)

	if not path.exists(output_video):
		makedirs(output_video)


	for e in list_frames:
		#print("idx: %d, src: %s/%s" % (e[0], e[1][0], e[1][1]))
		src_file = "%s/%s" % (e[1][0], e[1][1])
		dst_file = "/tmp/video/filename_%d.jpg" % e[0]
		
		copyfile(src_file, dst_file)

	p_run = ["/usr/bin/avconv", "-r", "10", "-i", "filename_%d.jpg", "-b:v", "1000k", video_name]
	pid = subprocess.Popen(p_run, cwd="/tmp/video")
	pid.wait()

	copyfile(video_tmp + video_name, output_video + "/" + video_name)
	rmtree(video_tmp)


if __name__ == '__main__':
	argc = len(sys.argv)
	if argc != 2:
		print("input folder not specified")
		sys.exit(1)
	
	rpath_in = sys.argv[1]
	if rpath_in[-1] == '/':
		rpath_in = rpath_in[0: len(rpath_in)-1]

	output_video = output_video + "/" + rpath_in[rpath_in.rfind("/")+1:]
	main(rpath_in)
