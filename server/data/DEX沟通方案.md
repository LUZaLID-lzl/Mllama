## DEX沟通方案

1、M11 A11 预编译的 dex优化是什么类型？包括A13的





2、background作speed dex优化，可能需要多长时间？





3、speed dex优化生成在super还是data？ 目前的结论是data。

```
目前看生成在data/dalvik-cache，但是原APK路径下没有odex文件。
后续如果多次触发background dex，检查pkg是否有做dex的时候，貌似是通过pkg的原路径下检查，这会导致每一次进行background dex都会触发一次pkgs全量优化
```



4、尝试定制background dex， 满足触发条件：浅度idle + 电量> 50%







测试细节：

| 触发方式                                              | 优化模式 | CPU使用详情(总800%)              | 总优化时间        |      |
| ----------------------------------------------------- | -------- | -------------------------------- | ----------------- | ---- |
| 息屏20分钟左右，通过广播触发dex2oat(非background dex) | speed    | 0%~800%之间都有，没有CPU上的限制 | 1579068ms ~ 26min |      |
| background dex                                        | speed    |                                  | 2050108ms         |      |
|                                                       |          |                                  |                   |      |

```
Running dexopt (dexoptNeeded=1) on: /product/priv-app/GoogleRestore/GoogleRestore.apk pkg=com.google.android.apps.restore isa=arm64 dexoptFlags=public,enable_hidden_api_checks targetFilter=speed oatDir=null classLoaderContext=PCL[]{PCL[/system/system_ext/framework/androidx.window.extensions.jar]#PCL[/system/system_ext/framework/androidx.window.sidecar.jar]}
```

```
Running dexopt (dexoptNeeded=-3) on: /product/app/MtkWallpaperPicker/MtkWallpaperPicker.apk pkg=com.android.wallpaperpicker isa=arm64 dexoptFlags=boot_complete,public,enable_hidden_api_checks targetFilter=speed oatDir=null classLoaderContext=PCL[]{PCL[/system/framework/android.test.base.jar]#PCL[/system/framework/android.hidl.manager-V1.0-java.jar]#PCL[/system/framework/android.hidl.base-V1.0-java.jar]}
```





Actions
\1. 调整启动dex优化的广播/消息 —— ODM/DL

```
由于需要尽可能早做dex并且稳定触发，目前看还是开机广播比较合适-现在采用开机广播加定时器的方式，目前定时器设置为10分钟
```

\2. 启动dex优化的等待时间衡量 —— ODM/DL

```
定时器加上收到开机广播的时间，大概是进入开机向导界面后，过11分钟左右开始执行bg_Dex，整个dex完成时间在35分钟左右
```

\3. 通知栏定义（参照升级）—— DL
实现通知栏 —— ODM

```
目前已添加通知栏,参照系统升级样式，通知栏不可移除，优化完成后自动移除
```

\4. 使用Backgroud dex优化的公开接口，尽可能定制新增speed接口 —— ODM

```
新增runBackgroundDexoptJobWithComplieFilter接口，通过Settings.Global传递参数
```

\5. 多次测试，确保不影响Scan2deploy等等 —— ODM/DL
\6. 升级上来的版本，确保也会做speed dex优化 —— ODM `明鑫7.beta1 升级 next ota升级时间长，1小时以上，调查原因 —— ODM/DL `明鑫
8.beta1 升级 beta2 时间长的问题仍然存在，需要beta2到next ota验证 —— 发布note @明鑫
