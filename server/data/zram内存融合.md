## ZRAM内存融合

**当前可以通过以下方式来配置内存融合：**

1：修改swap空间的大小

device/mediatek/common/fstab.enableswap

```
/dev/block/zram0 none swap defaults zramsize=1073741824
或者使用百分比进行配置
/dev/block/zram0 none swap defaults zramsize=60%
```



2：修改swappines的激进程度

swappines越大，内存压缩更频繁（上限100）

/device/mediatek/common/ago/init/init.ago_default.rc

    write /dev/memcg/memory.swappiness 50
    write /dev/memcg/apps/memory.swappiness 50
    write /dev/memcg/system/memory.  50
    write /proc/sys/vm/swappiness 50



**以下是内存融合详细的配置介绍：**

### 1：了解swap

swap可以认为是内存的扩充，最早的方案是从flash（闪存ROM）分出一块区域出来用作swap分区，当内存紧张时，kswapd就会被唤醒，但不是把应用程序杀掉，而是把lru中应用程序所占用的匿名内存数据交换到swap分区中，等切换回来的时候就可以直接把这部分数据恢复到内存当中，节省重新开启所需的时间。但是flash寿命有限一般10w次左右，如果频繁读写会损耗flash。

在zram swap 体系中，则直接在RAM中分配一块区域作为swap分析，而被放到swap分区的应用程序，所占用的内存使用zram技术压缩过的，比如，微信在普通内存中占用50MB的空间，如果压缩倍率为2.5，则放在swap分区里面的数据只需要50/2.5=20MB的空间，这样swap分区里面就可以存放更多后台临时不用的应用程序，变相扩展了内存的大小：

![](2023-10-31 09-55-58.png)

### 2、zram swap

zram 是linux内核的一项功能，可提供虚拟内存的压缩。 zram通过在RAM内压缩块设备上的分页，直到必须使用硬盘上的交换空间，以避免在磁盘上进行分页，从而提高性能。

特点是在RAM上开辟一段空间作为交换空间。

**主要优点：**

- 使用RAM作为交换空间，减少系统用于交换的I/O操作。
- 降低系统访问磁盘/Flash的次数，延长磁盘/Flash的使用寿命。

**主要缺点：**

-  频繁使用zram时，由于不断进行压缩和解压操作，会增加CPU loading。



### 3、动态调整zram相关参数以及常用方法：

**3.1 开启/关闭 swap分区**

/device/mediatek/common/ago/init/init.ago_default.rc（对 > 1G内存设备生效）

```
swapon_all /vendor/etc/fstab.enableswap
```

以上是在系统中设置，同时可以通过adb指令来开关(adb shell)：

swapon /dev/block/zram0

swapoff /dev/block/zram0



**3.2 注意事项**

在动态调整zram相关参数之前，**需要先关闭zram设备**，方法如下：

​	3.2.1 执行命令：cat /proc/swaps 查看设备路径：

![image-20231031100935971](image-20231031100935971.png)

​	3.2.2 执行命令：swapoff /dev/block/zram0 关闭该设备

​	3.2.3 再次执行 cat /proc/swaps 确认设备已经正常关闭：

![image-20231031101026477](image-20231031101026477.png)

​	下面已经没有显示zram0,说明已经正常关闭。

​	3.2.4 执行命令：echo 1 > /sys/block/zram0/reset 去reset zram

如上步骤做完之后，即可重新设定zram的其他参数。



**3.3 修改zram大小**

执行命令：echo **64M** > /sys/block/zram0/disksize 去设定zram大小。

1、上述方法只是动态设置zram大小，平台重启之后就会失效。如果需要永久设置，还需修改相关code:

device/mediatek/common/fstab.enableswap

```
/dev/block/zram0 none swap defaults zramsize=1073741824
或者使用百分比进行配置
/dev/block/zram0 none swap defaults zramsize=60%
```

 2、 zram 一般默认设置为系统总memory的50%，在小内存配置的项目中，建议将该值增大至65%左右，如2G项目中，将zram大小设置成1.3G。

 3、 zram swap虽然可以让小内存设备在多任务情况下切换自如，提高用户体验，但是在大内存设备中，则会因为不断复制内存并且CPU反复压缩解压从而拖慢速度。所以大内存项目中，zram的大小切勿设置过大。  



**3.4 查看swap信息**

指令：adb shell cat /proc/zraminfo	获取当前swap信息，如大小，算法等：

![image-20231031103512226](image-20231031103512226.png)

zram的压缩倍率可以通过OrigSize/ComprSize 计算  上述示例中 压缩倍率= 232468 / 57129 ~=4



**3.5 swappiness**

swappiness 代表swap out的激进性，值越大越倾向swap anon page to zram 来进行回收内存(swap分区使用率越高)， 值越小越倾向回收file page

swappiness有vm.swappiness 和memory.swappiness的区别。如果没有定义 **CONFIG_MEMCG**(该宏默认打开)，则使用前者，如有定义，则二者一同使用。

vm.swappiness决定的是全局页回收。该值为0时，只有在进行全局回收，并且file page+free page<=total_high_wmark时才进行匿名回收。

而memory.swappiness 该参数值则对当前cgroup生效，其功能和vm.swappiness一样，唯一的区别是，如果memory.swappiness设置成0，就算系统配置的有交换空间，当前cgroup也不会使用交换空间。

可以在以下位置修改swappines：

/device/mediatek/common/ago/init/init.ago_default.rc

```
    write /dev/memcg/memory.swappiness 100
    write /dev/memcg/apps/memory.swappiness 100
    write /dev/memcg/system/memory.  100
    write /proc/sys/vm/swappiness 100
```

注意swappiness 最大最小值定义 ， 如果定义最大值为 one_hundred , 则其取值范围为0～100，echo 大于100值 > /proc/sys/vm/swappiness 不会生效.

**建议**： 低内存项目将swappiness尽量设高，如上面示例的512 ago项目中，设置成180，而大内存项目则保持默认。

kernel-4.9/kernel/sysctl.c

```
		.procname	= "swappiness",
		.data		= &vm_swappiness,
		.maxlen		= sizeof(vm_swappiness),
		.mode		= 0644,
		.proc_handler	= proc_dointvec_minmax,
		.extra1		= &zero,
		.extra2		= &one_hundred,
```

