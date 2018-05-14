from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from .forms import  PostForm, GetForm
from .inference_pipeline_starter import InferencePipeline, JobEntry
from .gaussian_blur3d_starter import run_gaussian_blur3d
from .gaussian_blur3d_starter import pre_gaussian_blur3d
from .gaussian_blur3d_starter import post_gaussian_blur3d
import random
import re
import os
import threading
import logging

inference_pipeline = None
uid_dict = {}

# execute task after posting job, this task might last for a long time,
# so I use multithreading to carry this function.
def execute_task(job_name, uid, in_dir, out_dir):
    # uid_dict use to record the uid and if this task has finish running
    # if yes, it store True, if still running or failed, it store False
    # for this dictionary, its key is uid, value is a list include its state
    # and the output directory
    global  uid_dict
    try:
        uid_dict[uid] = [False, None]
        inference_pipeline.execute(job_name, in_dir, out_dir)
        logging.info('Back end task is done.')
        uid_dict[uid] = [True, out_dir]
    except Exception as e:
        uid_dict[uid] = [False, None]

# job service Post request
def job(request):
    if request.method == 'POST':
        # get parameter "job_name" and "in_dir" from post request
        job_name = request.POST.get('job_name', '')
        in_dir = request.POST.get('in_dir', '')
        out_dir = os.getcwd() + 'part3_backend/output_volume/'
        logging.info('job name: ', job_name, ' in dir: ', in_dir)
        # if this job_name was registered in our pipeline, so it is valid
        if inference_pipeline.is_job_registered(job_name):
            uid = "{:03}".format(random.randrange(1, 10 ** 3))
            # I set multithread for this task in order to get uid and return response firs,
            # because blurred image this function may last for a long time and cause timeout
            task = threading.Thread(target=execute_task, args=(job_name, uid, in_dir, out_dir,))
            task.start()
            return HttpResponse('<h1>Job ' + job_name + ' is executing... UID:' + uid + '</h1>', status=200)
        # else we should return a resource not found response
        else:
            return HttpResponseNotFound('<h1>Job not found</h1>', status=404)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>', status=404)

# query service Get request
def query(request):
    if request.method == 'GET':
        uid = request.path[request.path.find('query/') + 6:]
        # return resonse for four kind of cases: like has finishing running, failed, still running
        if uid not in uid_dict:
            return HttpResponseNotFound('<h1>Job uid not found</h1>', status=404)
        elif uid_dict[uid][0] is False:
            return HttpResponseNotFound('<h1>Job stilling running or failed with an error</h1>', status=404)
        return HttpResponse('<h1>Path to the result is ' + uid_dict[uid][1] + '</h1>')
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def index(request):
    # here I register 3dblur job as example to test post request
    global inference_pipeline
    job = JobEntry(name='3dblur', config={'sigma': 5.0},
                        preprocess=pre_gaussian_blur3d,
                        postprocess=post_gaussian_blur3d,
                        func=run_gaussian_blur3d)
    inference_pipeline = InferencePipeline([job])
    postform = PostForm()
    getform = GetForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            route = form.cleaned_data['route']
            # get job_name and in_dir from the path we input use regular experssion
            find = re.search(r".+?job_name=(.+?)&in_dir=(.+)", route)
            job_name = '' if find is None else find.group(1)
            find = re.search(r".+?job_name=(.+?)&in_dir=(.+)", route)
            in_dir = '' if find is None else find.group(2)
            out_dir = './'
            logging.info('job name: ', job_name, ' in dir: ', in_dir)
            if inference_pipeline.is_job_registered(job_name):
                uid = "{:03}".format(random.randrange(1, 10 ** 3))
                task = threading.Thread(target=execute_task, args=(job_name, uid, in_dir, out_dir,))
                task.start()
                return HttpResponse('<h1>Job ' + job_name + ' is executing... UID:' + uid + '</h1>', status=200)
            else:
                return HttpResponseNotFound('<h1>Job not found</h1>', status=404)

    if request.method == 'GET':
        global uid_dict
        form = GetForm(request.GET)
        if form.is_valid():
            route = form.cleaned_data['route']
            find = re.search(r".*?query[/](.+)", route)
            uid = '' if find is None else find.group(1)
            if uid not in uid_dict:
                return HttpResponseNotFound('<h1>Job uid not found</h1>', status=404)
            elif uid_dict[uid][0] is False:
                return HttpResponseNotFound('<h1>Job stilling running or failed with an error</h1>', status=404)
            return HttpResponse('<h1>Path to the result is ' + uid_dict[uid][1] + '</h1>')
    return render(request, 'index.html', {'postform': postform, 'getform': getform})
