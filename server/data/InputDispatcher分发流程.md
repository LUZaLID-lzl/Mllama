### InputDispatcher分发流程

问题背景：DL36待机界面插入WLC充电机器不会休眠



影响休眠的主要是PMS的userActivityNoUpdateLocked(long eventTime, int event, int flags, int uid)方法在不断的更新用户活动时间，导致
updateUserActivitySummaryLocked在执行灭屏计算的nextTimeout不断被更新。最终nextTimeout不可能小于当前时间，也就不可能会灭屏。
同时，此方法是通过native层传过来的，在PMS中唯一的native call

```java
    // Called from native code.
    private void userActivityFromNative(long eventTime, int event, int flags) {
        userActivityInternal(eventTime, event, flags, Process.SYSTEM_UID);
    }
```

通过查阅native层android_server_PowerManagerService_userActivity的调用逻辑。得知是在InputDispatcher.cpp中，当kernel接收到events之后，通过这个类的pokeUserActivity，传递到com_android_server_input_InputManagerService.cpp中，然后将事件更新传入到PMS中，保持屏幕活跃。

所以此问题的原因是由于WLC不断的上报事件，导致无法灭屏。

那么此片文章主要是梳理事件分发的机制以及流程：



### 概述

当输入设备可用时，Linux内核会在/dev/input/下创建对应的名为event0~n或其他名称的设备节点。
而当输入设备不可用时，则会将对应的节点删除。
Android输入系统的工作原理概括来说，就是监听/dev/input/下的所有设备节点，当某个节点有数据可读时，将数据读出并进行一系列的翻译加工，然后在所有的窗口中寻找合适的事件接收者，并派发给它

用adb shell getevent –t 可以查看当前按下按键的值，值0x01表示按下，0x00则表示抬起

事件类型（0001），事件代码（0074）以及事件的值（00000001）

![](2023-02-21_15-55.png)



**android系统input事件处理流程**

![](20190612095015690.png)

当kernel将事件信息写入设备节点时，InputReader通过EventHub不断的读取事件信息，并将其转化成为android的输入事件，并将其传输到InputDispatcher中，然后InputDispatcher根据WMS中的窗口信息，将不同的事件分发给相对应的窗口去响应。
而后窗口的ViewRootImpl对象再沿着控件树将事件派发给感兴趣的控件。控件对其收到的事件作出响应，更新自己的画面、执行特定的动作

- InputManagerService，一个Android系统服务，它分为Java层和Native层两部分。Java层负责与WMS的通信。而Native层则是InputReader和InputDispatcher两个输入系统关键组件的运行容器。
- EventHub，直接访问所有的设备节点。并且正如其名字所描述的，它通过一个名为getEvents()的函数将所有输入系统相关的待处理的底层事件返回给使用者。这些事件包括原始输入事件、设备节点的增删等。
- InputReader，是IMS中的关键组件之一。它运行于一个独立的线程中，负责管理输入设备的列表与配置，以及进行输入事件的加工处理。它通过其线程循环不断地通过getEvents()函数从EventHub中将事件取出并进行处理。对于设备节点的增删事件，它会更新输入设备列表于配置。对于原始输入事件，InputReader对其进行翻译、组装、封装为包含了更多信息、更具可读性的输入事件，然后交给InputDispatcher进行派发。
- WMS，虽说不是输入系统中的一员，但是它却对InputDispatcher的正常工作起到了至关重要的作用。当新建窗口时，WMS为新窗口和IMS创建了事件传递所用的通道。另外，WMS还将所有窗口的信息，包括窗口的可点击区域，焦点窗口等信息，实时地更新到IMS的InputDispatcher中，使得InputDispatcher可以正确地将事件派发到指定的窗口。



###  分发过程

```java
status_t InputDispatcher::start() {
    if (mThread) {
        return ALREADY_EXISTS;
    }
    mThread = std::make_unique<InputThread>(
            "InputDispatcher", [this]() { dispatchOnce(); }, [this]() { mLooper->wake(); });
    return OK;
}
...
void InputDispatcher::dispatchOnce() {
    nsecs_t nextWakeupTime = LONG_LONG_MAX;
    { // acquire lock
        std::scoped_lock _l(mLock);
        mDispatcherIsAlive.notify_all();

        if (!haveCommandsLocked()) {
            // 通过dispatchOnceInnerLocked进行输入事件分发，传出参数nextWakeupTime决定下次派发循环的时间点
            dispatchOnceInnerLocked(&nextWakeupTime);
        }

        // 执行命令队列中的命令
        if (runCommandsLockedInterruptible()) {
            // 设置nextWakeupTime为立即开始执行下次线程循环
            nextWakeupTime = LONG_LONG_MIN;
        }

        // 检查是否有事件等待事件过长，如果太长抛出ANR，并返回下次唤醒时间
        const nsecs_t nextAnrCheck = processAnrsLocked();
        nextWakeupTime = std::min(nextWakeupTime, nextAnrCheck);

        if (nextWakeupTime == LONG_LONG_MAX) {
            mDispatcherEnteredIdle.notify_all();
        }
    } // release lock

    // 计算需要休眠的时间timeoutMillis，并通过pollOnce进入epoll_wait
    nsecs_t currentTime = now();
    int timeoutMillis = toMillisecondTimeoutDelay(currentTime, nextWakeupTime);
    mLooper->pollOnce(timeoutMillis);
}
```

1.通过dispatchOnceInnerLocked进行输入事件分发，参数nextWakeupTime决定下次派发循环的时间点

2.执行命令队列中的命令，命令是一个符合Command签名的回调函数，可以通过InputDispatcher::postCommandLocked()创建并添加到命令队列mCommandQueue中，InputDispatcher执行命令的过程类似于Handler的工作方式

3.计算需要休眠的时间timeoutMillis，并通过pollOnce进入epoll_wait

线程执行Looper->pollOnce，进入epoll_wait等待状态，派发线程的休眠在三种情况下可能被唤醒：

- callback：epoll_wait监听的fd由epoll_event发生时唤醒
-  timeout：到达nextWakeupTime时间，超时唤醒
-  wake：主动调用Looper::wake函数唤醒（由输入事件注入派发对队列中）



**dispatchOnceInnerLocked**

```java
void InputDispatcher::dispatchOnceInnerLocked(nsecs_t* nextWakeupTime) {
    nsecs_t currentTime = now();

    //如果设备刚刚唤醒，重复动作
    if (!mDispatchEnabled) {
        resetKeyRepeatLocked();
    }

    //当分发被冻结，则不再处理超时和分发事件的工作，
    //setInputDispatchMode可以使InputDispatcher在禁用、冻结、正常状态切换
    if (mDispatchFrozen) {
        if (DEBUG_FOCUS) {
            ALOGD("Dispatch frozen.  Waiting some more.");
        }
        return;
    }
	
    //优化app切换延迟，当切换超时，则抢占分发，丢弃其他所有即将要处理的事件
    //如果isAppSwitchDue为true，说明没有及时响应HOME键等操作
    bool isAppSwitchDue = mAppSwitchDueTime <= currentTime;
    if (mAppSwitchDueTime < *nextWakeupTime) {
        *nextWakeupTime = mAppSwitchDueTime;
    }

    //如果还没有待分发的事件，去mInboundQueue中取出一个事件
    if (!mPendingEvent) {
        if (mInboundQueue.empty()) {
            //如果isAppSwitchDue为true，重置mAppSwitchDueTime为LONG_LONG_MAX
            if (isAppSwitchDue) {
                resetPendingAppSwitchLocked(false);
                isAppSwitchDue = false;
            }
			
            //如果currentTime超过下次需要重复执行的时间，合成一个重复的键mPendingEvent
            if (mKeyRepeatState.lastKeyEntry) {
                if (currentTime >= mKeyRepeatState.nextRepeatTime) {
                    mPendingEvent = synthesizeKeyRepeatLocked(currentTime);
                } else {
                    if (mKeyRepeatState.nextRepeatTime < *nextWakeupTime) {
                        *nextWakeupTime = mKeyRepeatState.nextRepeatTime;
                    }
                }
            }
			
            //此时还没有待分发的事件时，return
            if (!mPendingEvent) {
                return;
            }
        } else {
            //如果mInboundQueue不为空，取队列头部的EventEntry赋值给mPendingEvent
            //之所以用成员变量而不是局部变量保存，是由于此次线程循环有可能不能完成此事件派发
            mPendingEvent = mInboundQueue.front();
            mInboundQueue.pop_front();
            traceInboundQueueLengthLocked();
        }
		
        if (mPendingEvent->policyFlags & POLICY_FLAG_PASS_TO_USER) {
            //为该事件提醒用户界面做出反应
            pokeUserActivityLocked(*mPendingEvent);
        }
    }

    ALOG_ASSERT(mPendingEvent != nullptr);
    //检查事件是否需要丢弃，dropReason描述了是否需要被丢弃
    bool done = false;
    DropReason dropReason = DropReason::NOT_DROPPED;
    if (!(mPendingEvent->policyFlags & POLICY_FLAG_PASS_TO_USER)) {
        //在事件注入派发时调用interceptMotionBeforeQueueing询问派发测量，倘若派发策略不允许此事件被派发给用户，则丢弃
        dropReason = DropReason::POLICY;
    } else if (!mDispatchEnabled) {
        //如果InputDispatcher被禁用，通过setInputDispatchMode设置，则此事件也会被丢弃
    	//注意如果被冻结时时不会丢弃事件，而是等解冻后继续派发
        dropReason = DropReason::DISABLED;
    }

    if (mNextUnblockedEvent == mPendingEvent) {
        mNextUnblockedEvent = nullptr;
    }

    ALOGE("liziluo mPendingEvent->type:%d",mPendingEvent->type);

    //根据事件的类型进行分发
    switch (mPendingEvent->type) {
            //配置改变事件
        case EventEntry::Type::CONFIGURATION_CHANGED: {
            ConfigurationChangedEntry* typedEntry =
                    static_cast<ConfigurationChangedEntry*>(mPendingEvent);
            done = dispatchConfigurationChangedLocked(currentTime, typedEntry);
            dropReason = DropReason::NOT_DROPPED; // configuration changes are never dropped
            break;
        }
            //设备重置事件
        case EventEntry::Type::DEVICE_RESET: {
            DeviceResetEntry* typedEntry = static_cast<DeviceResetEntry*>(mPendingEvent);
            done = dispatchDeviceResetLocked(currentTime, typedEntry);
            dropReason = DropReason::NOT_DROPPED; // device resets are never dropped
            break;
        }
			//焦点事件
        case EventEntry::Type::FOCUS: {
            FocusEntry* typedEntry = static_cast<FocusEntry*>(mPendingEvent);
            dispatchFocusLocked(currentTime, typedEntry);
            done = true;
            dropReason = DropReason::NOT_DROPPED; // focus events are never dropped
            break;
        }
			
        case EventEntry::Type::KEY: {
            KeyEntry* typedEntry = static_cast<KeyEntry*>(mPendingEvent);
            if (isAppSwitchDue) {
                if (isAppSwitchKeyEvent(*typedEntry)) {
                    resetPendingAppSwitchLocked(true);
                    isAppSwitchDue = false;
                } else if (dropReason == DropReason::NOT_DROPPED) {
                    dropReason = DropReason::APP_SWITCH;
                }
            }
            if (dropReason == DropReason::NOT_DROPPED && isStaleEvent(currentTime, *typedEntry)) {
                dropReason = DropReason::STALE;
            }
            if (dropReason == DropReason::NOT_DROPPED && mNextUnblockedEvent) {
                dropReason = DropReason::BLOCKED;
            }
            done = dispatchKeyLocked(currentTime, typedEntry, &dropReason, nextWakeupTime);
            break;
        }

        case EventEntry::Type::MOTION: {
            MotionEntry* typedEntry = static_cast<MotionEntry*>(mPendingEvent);
            //事件因为home键没有能被及时响应丢弃
            if (dropReason == DropReason::NOT_DROPPED && isAppSwitchDue) {
                dropReason = DropReason::APP_SWITCH;
            }
            //事件因为过期丢弃
            if (dropReason == DropReason::NOT_DROPPED && isStaleEvent(currentTime, *typedEntry)) {
                dropReason = DropReason::STALE;
            }
            //事件因为阻碍了其他窗口获得事件丢弃
            if (dropReason == DropReason::NOT_DROPPED && mNextUnblockedEvent) {
                dropReason = DropReason::BLOCKED;
            }
            done = dispatchMotionLocked(currentTime, typedEntry, &dropReason, nextWakeupTime);
            break;
        }
    }

    if (done) {
		//如果事件丢弃，为了保证窗口收到的事件仍能保持down/up enter/exit的配对状态，还需要对事件进行补发zzzzzzz
        if (dropReason != DropReason::NOT_DROPPED) {
            ALOGE("liziluo DropReason:%d",dropReason);
            dropInboundEventLocked(*mPendingEvent, dropReason);
        }
        mLastDropReason = dropReason;
		//设置mPendingEvent对象为null，使在下次循环时可以处理派发队列中的下一条事件
        releasePendingEventLocked();
        //使得InputDispatcher能够快速处理下一个分发事件
        //因为当派发队列为空时，派发线程可能需要在下次循环中生成重复按键事件，因此不能直接进入休眠
        *nextWakeupTime = LONG_LONG_MIN; // force next poll to wake up immediately
    }
}
```

1. 如果派发队列为空，则回事派发线程陷入无期限休眠状态
1. InputDispatcher的冻结处理
如果当前InputDispatcher被冻结，则不进行派发操作，InputDispatcher有三种状态，分别是正常状态、冻结状态和禁用状态，可以通过InputDispatcher的setInputDispatchMode函数来设置
1. 窗口切换操作处理
mAppSwitchDueTime ，代表了App最近发生窗口切换操作时（比如按下Home键、挂断电话），该操作事件最迟的分发时间，当事件分发的时间点距离该事件加入mInboundQueue的时间超过500ms,则认为app切换过期,即isAppSwitchDue=true。
如果mAppSwitchDueTime小于nextWakeupTime（下一次InputDispatcherThread醒来的时间），就将mAppSwitchDueTime赋值给nextWakeupTime，这样当InputDispatcher处理完分发事件后，会第一时间处理窗口切换操作
1. 取出事件
如果没有待分发的事件，就从mInboundQueue中取出一个事件，如果mInboundQueue为空，并且没有待分发的事件，就return，如果mInboundQueue不为空，取队列头部的EventEntry赋值给mPendingEvent，mPendingEvent的类型为EventEntry对象指针
1. 事件丢弃
dropReason代表了事件丢弃的原因，它的默认值为DROP_REASON_NOT_DROPPED，代表事件不被丢弃。
根据mPendingEvent的type做区分处理，这里主要截取了对Motion类型的处理。经过过滤，会调用dispatchMotionLocked函数为这个事件寻找合适的窗口
1. 后续处理
执行dispatchMotionLocked进行Motion事件的派发，如果派发完成，无论成功派发还是事件被丢弃，都会返回true，否则返回false，在下次循环时再次尝试此事件派发。如果dispatchMotionLocked事件分发成功，则会调用releasePendingEventLocked函数，其内部会将mPendingEvent的值设置为Null，并将mPendingEvent指向的对象内存释放掉。将nextWakeupTime的值设置为LONG_LONG_MIN，这是为了让InputDispatcher能够快速处理下一个分发事件
1. 派发一个事件至少需要一次线程循环才能完成，因为事件的目标窗口有可能正在处理前一个输入事件，在窗口完成之前的事件的处理病给予反馈之前，InputDIspatcher不会在向此窗口派发新事件。
事件的派发是串行的，在队首的事件完成派发或者丢弃之前，不会对后续的事件进行派发
![](2023-02-27_16-38.png)

可分发的事件类型有五种分别是:

CONFIGURATION_CHANGED、	DEVICE_RESET、	FOCUS、	KEY、	MOTION

每种方法都有相对应的分发方法,且前三种事件不能被丢弃,一但执行就必须会分发下去,而KEY和MOTION会根据用户操作等来判断是否丢弃,当丢弃后则不会进行分发,重新从事件队列读出新的事件.那么当事件避开了丢弃判断之后,才能由InputDispatcher尝试派发.

以KEY类型事件为例,由dispatchKeyLocked尝试进行派发，它会根据键盘事件的类型，将键盘事件分发给相应的窗口，以便处理键盘事件。

这个方法首先检查按键是否可信，并且检查是否有重复按键发生，如果有则将重复次数存储到entry中，同时取消自己的下一个重复定时器，然后检查上次按键拦截的结果是否是要求重试，如果是则等待下次唤醒，否则给输入策略一个机会去拦截这个按键，然后检查拦截结果，如果拦截成功则查找焦点窗口，最后将按键分发给所有的目标。

**dispatchEventLocked**

```c++
void InputDispatcher::dispatchEventLocked(nsecs_t currentTime, EventEntry* eventEntry,
                                          const std::vector<InputTarget>& inputTargets) {
    ATRACE_CALL();
#if DEBUG_DISPATCH_CYCLE
    ALOGD("dispatchEventToCurrentInputTargets");
#endif

    ALOG_ASSERT(eventEntry->dispatchInProgress); // should already have been set to true
	 //向mCommandQueue队列添加doPokeUserActivityLockedInterruptible命令
    pokeUserActivityLocked(*eventEntry);
    for (const InputTarget& inputTarget : inputTargets) {
        //获取保存在mConnectionsByFd容器中的Connection
        sp<Connection> connection =
                getConnectionLocked(inputTarget.inputChannel->getConnectionToken());
        if (connection != nullptr) {
            //根据inputTarget，开始事件发送循环
            prepareDispatchCycleLocked(currentTime, connection, eventEntry, inputTarget);
        } else {
            if (DEBUG_FOCUS) {
                ALOGD("Dropping event delivery to target with channel '%s' because it "
                      "is no longer registered with the input dispatcher.",
                      inputTarget.inputChannel->getName().c_str());
            }
        }
    }
}
```

- 遍历inputTargets列表获取Connection的索引，再根据这个索引作为Key值来获取mConnectionsByFd容器中的Connection。
  调用prepareDispatchCycleLocked函数根据当前的inputTarget，开始事件发送循环。最终会通过inputTarget中的inputChannel来和窗口进行进程间通信，最终将Motion事件发送给目标窗口。
- 其中pokeUserActivityLocked(eventEntry)方法调用NativeInputManager::pokeUserActivity，最终会调用到Java层的PowerManagerService.java中的userActivityFromNative()方法． 这也是PMS中唯一的native call方法，此方法在PMS中会重置用户活动时间。



**pokeUserActivityLocked**

```c++
void InputDispatcher::pokeUserActivityLocked(const EventEntry& eventEntry) {
    if (eventEntry.type == EventEntry::Type::FOCUS) {
        // Focus events are passed to apps, but do not represent user activity.
        return;
    }
    int32_t displayId = getTargetDisplayId(eventEntry);
    sp<InputWindowHandle> focusedWindowHandle =
            getValueByKey(mFocusedWindowHandlesByDisplay, displayId);
    if (focusedWindowHandle != nullptr) {
        const InputWindowInfo* info = focusedWindowHandle->getInfo();
        if (info->inputFeatures & InputWindowInfo::INPUT_FEATURE_DISABLE_USER_ACTIVITY) {
#if DEBUG_DISPATCH_CYCLE
            ALOGD("Not poking user activity: disabled by window '%s'.", info->name.c_str());
#endif
            return;
        }
    }

    int32_t eventType = USER_ACTIVITY_EVENT_OTHER;
    switch (eventEntry.type) {
        case EventEntry::Type::MOTION: {
            const MotionEntry& motionEntry = static_cast<const MotionEntry&>(eventEntry);
            if (motionEntry.action == AMOTION_EVENT_ACTION_CANCEL) {
                return;
            }

            if (MotionEvent::isTouchEvent(motionEntry.source, motionEntry.action)) {
                eventType = USER_ACTIVITY_EVENT_TOUCH;
            }
            break;
        }
        case EventEntry::Type::KEY: {
            const KeyEntry& keyEntry = static_cast<const KeyEntry&>(eventEntry);
            if (keyEntry.flags & AKEY_EVENT_FLAG_CANCELED) {
                return;
            }
            eventType = USER_ACTIVITY_EVENT_BUTTON;
            break;
        }
        case EventEntry::Type::FOCUS:
        case EventEntry::Type::CONFIGURATION_CHANGED:
        case EventEntry::Type::DEVICE_RESET: {
            LOG_ALWAYS_FATAL("%s events are not user activity",
                             EventEntry::typeToString(eventEntry.type));
            break;
        }
    }
	
    std::unique_ptr<CommandEntry> commandEntry =
            std::make_unique<CommandEntry>(&InputDispatcher::doPokeUserActivityLockedInterruptible);
    commandEntry->eventTime = eventEntry.eventTime;
    commandEntry->userActivityEventType = eventType;
    postCommandLocked(std::move(commandEntry));
}
```

后续通过startDispatchCycleLocked方法，启动新的输入调度周期。该方法将处理所有InputDispatcher队列中的输入事件，并将其发送到相应的输入接收器。

