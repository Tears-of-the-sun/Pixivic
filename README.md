# Pixivic
a spider for Pixivic

My code is designed to complete a specific function, if there is any incorrectness or unsatisfactory place, please forgive me, leave your suggestions or hope.
To modify the specific parameters, please refer to the 'setting.txt' 
Use Leader to start!
Execute using the command line.
Install third-party module requests before using it.
For more compatibility， bloomfilter is annotated，if you wang to use,please note.
(Data is removed by additional use of a Bloon filter, you can install pybloom-live)

The request header has timeliness, and the failure is informed in time

新人，多多关照
采用requests模块，命令行形式运行leader.py
布隆过滤器给注释掉了，如果安装了pybloom-live可以使用，去除重复图片的效果更好。
查看settings.txt以修改参数
由于pixivic登录才有数据，请求头具有时效性，失效及时联系，给封了可就没了。
代码中限制了多线程(前面跑的时候因为太快已经被封了一个了)，setting里的参数能不该改尽量别改

新人，轻点~
