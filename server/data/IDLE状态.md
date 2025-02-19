**DeviceIdleController**是Doze模式的主要驱动。接下来，我将使用***device idle mode\***而不是***doze mode\***来描述“Doze”，因为它更符合代码的实际情况。如果你已经阅读了官方文档，你可能已经注意到下面的命令，开发者可以通过这些命令得知当下设备的应用行为：

```html
adb shell dumpsys battery unplug
adb shell dumpsys deviceidle step
```

对于上面的命令你可能并不熟悉，**dumpsys**是用来与系统服务交互的（查看它们的状态），**deviceidle**是我们之前没有看到过的，它是一个新的系统服务。

```html
$ adb shell service list | grep deviceidle
59  deviceidle: [android.os.IDeviceIdleController]
```



这个新的服务常驻以监听下面的系统事件，这些事件会触发系统是否进入idle mode：

1. 亮屏/暗屏
2. 充电状态
3. 重要的手势检测

**DeviceIdleController**维持着设备包含的五种状态：

1. **ACTIVE** – 设备在使用中，或者连接着电源。
2. **INACTIVE** – 设备已经从ACTIVE状态中出来一段时间了（使用者关闭了屏幕或者拔掉了电源）
3. **IDLE_PENDING** – 请留意，我们将进入idle mode.
4. **IDLE** – 设备进入idle mode.
5. **IDLE_MAINTENANCE** – 应用窗口已经打开去做处理.

当设备被唤醒和正在使用中，控制器就处于**ACTIVE**状态，外部的事件（不活跃时间超时，用户关闭屏幕，等等）将会使设备状态进入到**INACTIVE**. 那时，**DeviceIdleController**将会通过**AlarmManager**来设置他自己的alarm来驱动进程：

1. 一个alarm会被设置在一个预设的时刻（这个时间在M的预览中是30分钟）。
2. 当这个alarm生效后，**DeviceIdleController** 会进入到**IDLE_PENDING**然后再次设置同样的alarm。
3. 当触发下一个alarm后，控制器会进入到**IDLE** 状态，进入到这个状态后，应用特性会被完全限制。
4. 再向前推进这个服务会在**IDLE** 和**IDLE_MAINTENANCE**两个状态之间周期性的跳转，后者在服务完全被禁前，等待的应用事件被触发。

正如上面提到的，开发者能够使用下面的命令，手动地改变设备的这些状态：



```html
$ adb shell dumpsys deviceidle step
```





stepLightIdleStateLocked

从这段代码可以看出在LightDoze进入IDLE状态或退出IDLE状态时时，首先通知PMS、NetworkPolicyManager设置DeviceIdleMode为true或false，然后发送一个Intent为mLightIdleIntent的广播

当LightDoze进入IDLE/MAINTENANCE状态时，在Handler中：

    1.通知NetworkPolicyManagerService限制/打开网络；
    2.发送广播，DeviceIdleJobsController中进行接受，限制/运行JobService.
JobService与JobIntentService的关系类似于Service与IntentService的关系。JobService是在主线程中运行的，而JobIntentService会为每一次启动都准备一个子线程并在其中运行。

Service与InentService会因为App的停运而中止，而JobService与IntentService在App停运后会继续运行。

    JobService：适用于 Android 5.0（API 级别 21）及更高版本。onStartJob()是异步执行的，你需要在作业完成时调用jobFinished()方法来通知系统。这使得你能够在后台线程中执行长时间运行的任务。
    JobIntentService：在 Android 8.0（API 级别 26）之前提供向后兼容性，使得你可以在更旧的设备上使用 JobScheduler (作业调度)的功能。onHandleWork()方法在一个独立的工作线程中执行，并且在所有任务完成后会自动停止服务，不需要手动调用stopSelf()或者stopSelfResult()。


        //in this time 
        //we may can try to excute dex for preload apps
        //maybe into idle status will be later 
        android.util.Log.d("liziluo","i will send a reload dex Broadcast");
        Intent intent = new Intent("android.content.pm.action.DEVICE_IDLE_RELOAD_DEX");
        getContext().sendBroadcastAsUser(intent, UserHandle.SYSTEM);



    static final int LIGHT_STATE_ACTIVE = 0;
    /** Device is inactive (screen off) and we are waiting to for the first light idle. */
    @VisibleForTesting
    static final int LIGHT_STATE_INACTIVE = 1;
    /** Device is in the light idle state, trying to stay asleep as much as possible. */
    @VisibleForTesting
    static final int LIGHT_STATE_IDLE = 4;
    /** Device is in the light idle state, we want to go in to idle maintenance but are
     * waiting for network connectivity before doing so. */
    @VisibleForTesting
    static final int LIGHT_STATE_WAITING_FOR_NETWORK = 5;
    /** Device is in the light idle state, but temporarily out of idle to do regular maintenance. */
    @VisibleForTesting
    static final int LIGHT_STATE_IDLE_MAINTENANCE = 6;
    /** Device light idle state is overridden, now applying deep doze state. */
    @VisibleForTesting
    static final int LIGHT_STATE_OVERRIDE = 7;