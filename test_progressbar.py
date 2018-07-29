'''
测试进度条 类
'''
import time
import progressbar

total = 1000  
  
def dosomework():  
    time.sleep(0.01)  
            
progress = progressbar.ProgressBar()  
for i in progress(range(10)):  
    dosomework()  

pbar = progressbar.ProgressBar(maxval=16).start()  
for i in range(16):  
    pbar.update(i)  
    #print(i, "     \n")
    time.sleep(1)  
pbar.finish()  
