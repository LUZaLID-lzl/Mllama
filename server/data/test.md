android.hardware.camera2:

```
CameraManager.openCamera()
CameraCaptureSession.capture()
CameraDevice.createCaptureRequest()
```





android.hardware.Camera

```
    private static final String FACTORY_OPEN_FLASH = "com.mbw.testcase.factory.openflash";
    private final Handler factoryHandler = new Handler();

    //[296649]The back camera test defaults to flash light turned off
    public void sendDelayedBroadcast(Context context) {
        factoryHandler.postDelayed(() -> {
            android.util.Log.d("Factory", "send delay factoryHandler");
            Intent intent = new Intent(FACTORY_OPEN_FLASH);
            context.sendBroadcast(intent);
        }, 1000); // 延迟1秒发送广播
    }
    //[296649]The back camera test defaults to flash light turned off
    sendDelayedBroadcast(this);
```

```
import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.Context;

private static final String FACTORY_OPEN_FLASH = "com.mbw.testcase.factory.openflash";
private IntentFilter factoryFilter;

        factoryFilter = new IntentFilter(FACTORY_OPEN_FLASH);
        app.getActivity().getApplicationContext().registerReceiver(factoryReceiver, factoryFilter);
        
        
            //[296649]The back camera test defaults to flash light turned off
    BroadcastReceiver factoryReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            // 处理广播事件
            if (FACTORY_OPEN_FLASH.equals(intent.getAction())) {
                android.util.Log.d("Factory", "GNSS FACTORY_OPEN_FLASH GET");
                openFlash();
            }
        }
    };

    public void openFlash(){
        String value = FLASH_ON_VALUE;
        mApp.getAppUi().hideQuickSwitcherOption();
        updateFlashEntryView(value);
        mFlash.onFlashValueChanged(value);
    }
    //[296649]The back camera test defaults to flash light turned off
```



相机行为对比：

pre版本：进入相机测试默认打开闪光灯，同时预览相机界面，点击下方拍照按钮后，即可显示拍照完成的图片，确认无误后可以点击PASS FAIL按钮。

当前版本：进入相机测试后会启动系统相机，不会默认打开闪光灯，可以点击右上方按钮打开，点击拍照后，需要确认是否选择当前图片。
点击√按钮，会将图片结果返回给工模界面，这时可以点击PASS FAIL按钮。
点击x按钮，则会重新取景。

同时，点击返回按钮会回到工模，这时工模会处于黑屏状态。



```
dl36 	2022/7 -> 2023/11
xqt406	2022/11 -> 2024/2
xqt521_pie_dev  2023/9 -> 2023/11
xqt554_s_dev 	2023/10 -> 2024/1
dl36_t_sys_dev 2023/11 -> 2024/8
M63 2023/5 -> 2023/6
RS10 2024/6 -> 2024/11
```





```
25电量 无TIPS 

11-09 14:00:10.188  2090  8426 D liziluo : mBatteryInfo.batteryLevel: 25
11-09 14:00:10.188  2090  8426 D liziluo : mWarningLevel: 20
11-09 14:00:10.188  2090  8426 D liziluo : mBatteryInfo.remainingTimeUs: 0
11-09 14:00:10.188  2090  8426 D liziluo : lowBatteryEnabled: true
11-09 14:00:10.188  2090  8426 D liziluo : lowBatteryEnabled: true
11-09 14:00:10.188  2090  8426 D liziluo : ----------------------------------------
11-09 14:00:10.188  2090  8426 D liziluo : lowBatteryEnabled: true
11-09 14:00:10.188  2090  8426 D liziluo : dischargingLowBatteryState: false
11-09 14:00:10.188  2090  8426 D liziluo : mPolicy.testLowBatteryTip: false
11-09 14:00:10.188  2090  8426 D liziluo : mBatteryInfo.discharging: true
11-09 14:00:10.188  2090  8426 D liziluo : lowBattery: false
11-09 14:00:10.188  2090  8426 D liziluo : state: 2
```

