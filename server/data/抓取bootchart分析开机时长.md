

1.在ubuntu中安装bootchart

```
1.sudo apt-get update
 
2.sudo apt-get upgrade
 
3.
//ubuntu18.04上面找不到这个
//sudo apt-get install bootchart
//可以安装这一个
sudo apt-get install pybootchartgui

//ubuntu20.04上请用这个
sudo apt-get install systemd-bootchart
```

2.通过安卓自带的bootchart工具来获取开机启动数据

```
//进入adb shell
adb shell 
//获取root权限
su
//使能bootchart以支持获取启动数据
touch /data/bootchart/enabled
//重启安卓系统
reboot
 
//等待重启之后，建立连接
 
//进入adb shell
adb shell
//获取root权限
su
//进入bootchart目录下
cd /data/bootchart/
//将刚才bootchart获取到的数据打包
tar -czf bootchart.tgz enabled header proc_diskstats.log proc_ps.log proc_stat.log
//退出root权限
exit
//退出adb shell
exit
//获取安卓系统中刚才打包好的数据，放在你想要放的路径下
adb pull /data/bootchart/bootchart.tgz  /home/xxx
//进入该路径
cd /home/xxx
//使用bootchart命令生成图片
bootchart bootchart.tgz
```

一般来说，当你看到如下代码的时候，就证明成功了

```
swy@ubuntu:~$ bootchart bootchart.tgz
parsing 'bootchart.tgz'
parsing 'enabled'
parsing 'header'
parsing 'proc_diskstats.log'
parsing 'proc_ps.log'
warning: no parent for pid '2' with ppid '0'
parsing 'proc_stat.log'
merged 0 logger processes
pruned 36 process, 0 exploders, 7 threads, and 0 runs
False
bootchart written to 'bootchart.png'
```

但是在某种情况下，也会出现一些错误，比如说折磨了我一上午的

ZeroDivisionError: float division by zero

    Traceback (most recent call last)
      File "/usr/bin/bootchart", line 23, in <module>
        sys.exit(main())
      File "/usr/lib/python2.7/dist-packages/pybootchartgui/main.py", line 137, in main
        render()
      File "/usr/lib/python2.7/dist-packages/pybootchartgui/main.py", line 128, in render
        batch.render(writer, res, options, filename)
      File "/usr/lib/python2.7/dist-packages/pybootchartgui/batch.py", line 41, in render
        draw.render(ctx, options, *res)
      File "/usr/lib/python2.7/dist-packages/pybootchartgui/draw.py", line 282, in render
        draw_chart(ctx, IO_COLOR, True, chart_rect, [(sample.time, sample.util) for sample in disk_stats], proc_tree)
      File "/usr/lib/python2.7/dist-packages/pybootchartgui/draw.py", line 201, in draw_chart
        yscale = float(chart_bounds[3]) / max(y for (x,y) in data)
    ZeroDivisionError: float division by zero

我在网上找了很多方法，最终科学上网之后，终于找到了

sudo vim /usr/lib/python2.7/dist-packages/pybootchartgui/draw.py

进到这个文件里，修改第200行和201行的代码

    200         xscale = float(chart_bounds[2]) / max(0.00001, max(x for (x,y) in data))
    201         yscale = float(chart_bounds[3]) / max(0.00001, max(y for (x,y) in data))

linux 查看文件的行标的命令：

vi命令进入该文件之后，输入如下命令，回车即可

：set nu

然后替换完成之后，再重新执行bootchart命令即可

说明：

使用bootchart需要注意的是

1.ubuntu环境需要安装bootchart，安装完成后输入

bootchart --version

如果可以看到bootchart的版本即可 

2.一定要确保自己的安卓系统上有bootchart，这个绝大部分的安卓系统中都有的，但是并不是默认启动的，大家在按照上面的指令一步步走的时候，如果哪个指令出现了找不到文件或者找不到路径，那么首先需要确定是否安卓系统中已经安装了bootchart，且是否启动了。