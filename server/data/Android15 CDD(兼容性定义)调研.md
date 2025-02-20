# <u><font color="#00b050">此文章仅记录Android15新增变化</font></u>
## 2. 设备类型
### 2.2. 手持设备相关要求
#### 2.2.1. 硬件
支持蓝牙 LE 的手持设备实现：
- ~~[[7.4.3/H] 应支持蓝牙和蓝牙 LE。~~
- ~~[[7.4.3/H-0-1] 必须支持蓝牙和蓝牙 LE。~~
- <font color="#00b050">[[7.4.3/H-SR-1] 强烈建议支持蓝牙 LE 数据包长度扩展。</font>
- **注意**：在未来的 Android 版本中，[<font color="#00b050">7.4.3/H-SR-1</font>] 这项要求将成为必须满足的要求。

[7.7.1/H-1-1]（2023 年 12 月 11 日预览版）：
如果手持设备实现包含~~支持~~在外围设备模式下运行的控制器的 USB 端口，则：
```
- [7.7.1/H-1-1] 必须实现 Android Open Accessory (AOA) API。
```

[5.6/H-1-1 和 5.6/H-1-2]（2024 年 2 月 5 日预览版）：
对于声明 `android.hardware.audio.output` 和 `android.hardware.microphone` 的手持设备实现，请参阅第 [5.6](https://source.android.com/docs/compatibility/15/android-15-cdd?hl=zh-cn#56_audio-latency) 节中的 RTL 和 TTL 要求。
```
点按与发声间延迟时间 (TTL)，由 CTS 验证程序测量得出，是从用户点按屏幕，到通过扬声器听到点按操作产生的声音，中间经过的时间。这是使用 AAudio 原生音频 API 针对输出进行 5 次测量得出的平均值。

往返延迟时间 (RTL)，由 CTS 验证程序测量得出，是使用 AAudio 原生音频 API 在环回路径（将输出回馈到输入）上进行 5 次测量得出的平均连续延迟时间。环回路径是：

    扬声器/麦克风：内置扬声器到内置麦克风。
    模拟：3.5 毫米模拟耳机插孔和一个环回适配器。
    USB：USB 转 3.5 毫米适配器和环回适配器，或 USB 音频接口和环回线。

```
#### 2.2.5. 安全模型
[9.10/H–1–1]（2024 年 2 月 26 日预览版）
启动时验证是一项旨在保证设备软件完整性的功能。 如果设备实现支持该功能，则：
```
[9.10/H–1–1] 必须验证在 Android 启动序列期间加载的所有只读分区。

注意：如果设备实现已在不支持 9.10/C-1-8 至 C-1-12 的情况下搭载早期 Android 版本，且无法通过系统软件更新来添加对这些要求的支持，则可以不遵守这些要求。

```

#### 2.2.7. 手持设备媒体性能等级
##### 2.2.7.1. 媒体
如果手持设备实现针对 `android.os.Build.VERSION_CODES.MEDIA_PERFORMANCE_CLASS` 返回 `android.os.Build.VERSION_CODES.V`则
```
[5.1/H-1-1] 必须通过 `CodecCapabilities.getMaxSupportedInstances()` 和 `VideoCapabilities.getSupportedPerformancePoints()` 方法通告可以采用任何编解码器组合形式并行运行的硬件视频解码器会话的数量上限。
```
[5.1/H-1-2]（2024 年 2 月 5 日预览版）
- [5.1/H-1-2] 必须支持 6 个 8 位 (SDR) 硬件视频解码器会话实例（AVC、HEVC、VP9、AV1 或更高版本）采用任何编解码器组合形式并行运行，其中 3 个会话采用 1080p@30fps 分辨率，3 个会话采用 4K@30fps 分辨率，AV1 除外。<font color="#00b050">**对于所有会话，每秒丢失的帧数不得超过 1 帧**</font>。AV1 编解码器仅需要支持 1080p 分辨率，但仍需要支持 6 个分辨率为 1080p30fps 的实例。

5.1/H-1-4（2024 年 2 月 5 日预览版）
- [5.1/H-1-4] 必须支持 6 个 8 位 (SDR) 硬件视频编码器会话实例（AVC、HEVC、VP9、AV1 或更高版本）采用任何编解码器组合形式并行运行，其中 4 个会话采用 1080p@30fps 分辨率，2 个会话采用 4K@30fps 分辨率，AV1 除外。<font color="#00b050">**对于所有会话，每秒丢失的帧数不得超过 1 帧**</font>。AV1 编解码器仅需要支持 1080p 分辨率，但仍需要支持 6 个 1080p30fps 分辨率的实例。

5.1/H-1-6（2024 年 2 月 5 日预览版）
- [5.1/H-1-6] 必须支持 6 个 8 位 (SDR) 硬件视频解码器和硬件视频编码器会话实例（AVC、HEVC、VP9、AV1 或更高版本）采用任何编解码器组合形式并行运行，其中 3 个会话采用 4K@30fps 分辨率（AV1 除外），最多有 2 个是编码器会话，3 个会话采用 1080p 分辨率。<font color="#00b050">**对于所有会话，每秒丢失的帧数不得超过 1 帧**</font>。AV1 编解码器仅需要支持 1080p 分辨率，但仍需要支持 6 个 1080p30fps 分辨率的实例。

5.1/H-1-19（2024 年 2 月 5 日预览版）
- [5.1/H-1-19] 必须支持 3 个 10 位 (HDR) 硬件视频解码器和硬件视频编码器会话实例（AVC、HEVC、VP9、AV1 或更高版本）采用任何编解码器组合形式并行运行，并且均采用 4K@30fps 分辨率（AV1 除外），其中最多有 1 个编码器会话，该会话可通过 GL Surface 以 RGBA_1010102 输入格式进行配置。<font color="#00b050">**对于所有会话，每秒丢失的帧数不得超过 1 帧**</font>。如果从 GL Surface 进行编码，则无需由编码器生成 HDR 元数据。AV1 编解码器会话仅需要支持 1080p 分辨率，即使要求支持 4K 也是如此。

5.1/H-1-9（2024 年 2 月 5 日预览版）
- [5.1/H-1-9] 必须支持 2 个安全硬件视频解码器会话实例（AVC、HEVC、VP9、AV1 或更高版本）采用任何编解码器组合形式并行运行，并且 8 位 (SDR) 内容和 10 位 HDR 内容均采用 4k@30fps 分辨率（AV1 除外）。<font color="#00b050">**对于所有会话，每秒丢失的帧数不得超过 1 帧**</font>。AV1 编解码器会话仅需要支持 1080p 分辨率，即使要求支持 4K 也是如此。

5.1/H-1-10（2024 年 2 月 5 日预览版）
- [5.1/H-1-10] 必须支持 3 个非安全硬件视频解码器会话实例与 1 个安全硬件视频解码器会话实例（共 4 个实例，AVC、HEVC、VP9、AV1 或更高版本）采用任何编解码器组合形式并行运行，其中 3 个会话采用 4K@30fps 分辨率（AV1 除外）（包括 1 个安全解码器会话），1 个非安全会话采用 1080p@30fps 分辨率（其中最多有 2 个会话可以采用 10 位 HDR）。<font color="#00b050">**对于所有会话，每秒丢失的帧数不得超过 1 帧**</font>。AV1 编解码器会话仅需要支持 1080p 分辨率，即使要求支持 4K 也是如此。

[5.1/H-1-14]（2024 年 2 月 5 日预览版）
- [5.1/H-1-14] 必须支持 AV1 硬件解码器 Main 10, Level 4.1 ~~和胶片颗粒<font color="#00b050">~~**在采用 GPU 合成时可实现胶片颗粒效果</font>。**

[5.1/H-1-21]（2024 年 2 月 5 日预览版）
- [5.1/H-1-21] <font color="#00b050">**对于所有硬件视频解码器（AVC、HEVC、VP9、AV1 或更高版本），都必须支持 `FEATURE_DynamicColorAspect`。注意：这意味着应用可以在解码会话期间更新视频内容的颜色方面。在 Surface 模式下，支持 10 位和 8 位内容的解码器必须支持在 8 位和 10 位内容之间动态切换。支持 HDR 传输功能的解码器必须支持在 SDR 和 HDR 内容之间动态切换。**</font>

[5.1/H-1-22]（2024 年 2 月 5 日预览版）
- [5.1/H-1-22] <font color="#00b050">**对于摄像头支持的最高分辨率或 4K（以较低者为准），必须支持编码、解码、GPU 编辑和以纵向宽高比显示视频内容，而无论旋转元数据是什么。注意：这包括 HDR 配置文件，但前提是编解码器支持 HDR。AV1 编解码器仅需要支持 1080p 分辨率。此要求仅适用于硬件编解码器、GPU 和 DPU。**</font>

[5.1/H-1-20]（2024 年 2 月 5 日预览版）
- [5.1/H-1-20] <font color="#00b050">**在 4K 分辨率或摄像头支持的最高分辨率（以较低者为准）下，对于设备上存在的所有硬件 AV1 和 HEVC 编码器，都必须支持 [`Feature_HdrEditing`](https://developer.android.com/reference/android/media/MediaCodecInfo.CodecCapabilities?hl=zh-cn#FEATURE_HdrEditing) 功能。**</font>

如果手持设备实现针对 android.os.Build.VERSION_CODES.MEDIA_PERFORMANCE_CLASS 返回 android.os.Build.VERSION_CODES.V，并且支持硬件 AVC 或 HEVC 编码器，则：
- [5.2/H-2-1]<font color="#00b050"> **必须满足硬件 AVC 和 HEVC 编解码器的视频编码器速率失真曲线所定义的最低质量目标，如[运行性能等级 14 (PC14) - 视频编码质量 (VEQ) 测试](https://source.android.com/docs/compatibility/cts/media-cts?hl=zh-cn#run-pc14veq-cts)中所定义。**</font>

[5.2/H-2-2]（2024 年 2 月 5 日预览版）
- [5.2/H-2-2] <font color="#00b050">**必须使用 dav1d 软件 AV1 解码器以 1080p (>= 60 FPS) 的分辨率呈现示例视频**</font>


##### 2.2.7.2. 摄像头
[7.5/H-1-1]（2024 年 2 月 26 日预览版）
- [7.5/H-1-1] 必须具有一个主后置摄像头，该摄像头的分辨率必须至少为 1200 万像素，并且该摄像头必须支持以 4k@30fps、<font color="#00b050">**1080p@60fps 和 720p@60fps**</font> 拍摄视频。主后置摄像头是具有最低摄像头 ID 的后置摄像头。

[7.5/H-1-18]（2024 年 2 月 5 日预览版）
- [7.5/H-1-18] <font color="#00b050">**对于主后置摄像头和主前置摄像头，必须支持 JPEG_R。**</font>

[7.5/H-1-19]（2024 年 4 月 8 日预览版）
- [7.5/H-1-19]<font color="#00b050"> **采用最大尺寸 16:9 宽高比 JPEG 预览 1080p HLG10 视频时必须支持 CONTROL_VIDEO_STABILIZATION_MODE_PREVIEW_STABILIZATION；对于主后置摄像头，必须支持采用最大尺寸的 16:9 宽高比 JPEG 流组合预览 720p HLG10 视频。**</font>

[7.5/H-1-20]（2024 年 4 月 8 日预览版）
- [7.5/H-1-20] <font color="#00b050">**默认情况下，必须针对原生相机应用中的主后置摄像头和主前置摄像头输出 JPEG_R。**</font>

##### 2.2.7.3. 硬件
[7.1.1.3/H-2-1]（2024 年 2 月 5 日预览版）
- [7.1.1.3/H-2-1] <font color="#00b050">**如果设备屏幕宽度 小于 600 dp**</font>，屏幕密度必须至少为 400 dpi。

[7.6.1/H-2-1]（2024 年 4 月 8 日预览版）
- [7.6.1/H-2-1] 必须具有至少 8 GB 的物理内存，<font color="#00b050">**其中至少 6.64 GB 可供内核使用**</font>，如 android.app.ActivityManager.MemoryInfo 所报告。

##### 2.2.7.5. 显卡
如果手持设备实现针对 `android.os.Build.VERSION_CODES.MEDIA_PERFORMANCE_CLASS` 返回 `android.os.Build.VERSION_CODES.V`，则：
    [7.1.4.1/H-1-1] <font color="#00b050">此要求已从 Android 15（AOSP 实验版）中撤销。</font>
    [7.1.4.1/H-1-2] <font color="#00b050">必须支持 EGL_IMG_context_priority 和 EGL_EXT_protected_content 扩展。</font>
    [7.1.4.1/H-1-3] <font color="#00b050">必须支持 VkPhysicalDeviceProtectedMemoryFeatures.protectedMemory 和 VK_KHR_global_priority。</font>


### 2.3. TV 设备相关要求
#### 2.3.3. 软件
[3/T-0-2, 3/T-0-3. 3/T-1-1]（2024 年 2 月 26 日预览版）

```
Android TV 输入框架 (TIF) 能够简化向 Android TV 设备传输实时内容的过程。TIF 提供了一个标准 API，用于创建可控制 Android TV 设备的输入模块。

TV 设备实现：

    [3/T-0-2] 必须声明平台功能 android.software.live_tv。
    [3/T-0-3] 必须支持所有 TIF API，以便用户在设备上安装和使用利用此类 API 和基于 TIF 的第三方输入 服务的应用。

Android TV 调谐器框架 (TF) [2024 年第三季度前链接待定] 统一了 Android TV 设备上来自调谐器的直播内容与来自 IP 的流式传输内容的处理方式。调谐器框架提供了一个标准 API，用于创建使用 Android TV 调谐器的输入服务。

如果设备实现支持调谐器，则：

    [3/T-1-1] 必须支持所有调谐器框架 API，以便使用这些 API 的应用可以在设备上安装和使用。

```

### 2.5. Automotive 设备相关要求
#### 2.5.3. 软件
[3.14/A-0-8]（2024 年 4 月 8 日预览版）
- [3.14/A-0-8] <font color="#00b050">必须向非经过防分心优化的应用提供对 ActivityBlockingActivity 中和主屏幕上的媒体控件的访问权限</font>。

## 3. 软件
### 3.1. 受管理 API 兼容性
[C-0-8]（2024 年 4 月 8 日预览版）
- [C-0-8] 不得支持安装目标 API 级别低于<font color="#00b050"> **24**</font> 的应用。
### 3.3. 原生 API 兼容性
#### 3.3.1. 应用二进制接口
[C-0-6]（2024 年 2 月 26 日预览版）
- [C-0-6] 必须（通过上述参数）报告以下 ABI 列表的子集，不得报告列表中没有的 ABI。
- `armeabi`（NDK 不再支持将其作为目标）
- [`armeabi-v7a`](https://developer.android.com/ndk/guides/abis?hl=zh-cn#v7a)
- [`arm64-v8a`](https://developer.android.com/ndk/guides/abis?hl=zh-cn#arm64-v8a)
- [`x86`](https://developer.android.com/ndk/guides/abis?hl=zh-cn#x86)
- [`x86-64`](https://developer.android.com/ndk/guides/abis?hl=zh-cn#86-64)
- <font color="#00b050">riscv64</font>
### 3.8. 界面兼容性
#### 3.8.3. 通知
##### 3.8.3.4. 敏感通知保护
[3.8.3.4 敏感通知保护]（2024 年 4 月 8 日预览版）
```
设备实现：
    [C-1-1] 必须包含通知助理服务 (NAS)，用于隐去通知内容中发送给通知监听器的敏感信息，除非该服务是：
        uid 小于 10000 的系统签名应用
        System UI
        Shell
        指定的配套设备应用（由 CompanionDeviceManager 定义）
        `SYSTEM_AUTOMOTIVE_PROJECTION` role
        `SYSTEM_NOTIFICATION_INTELLIGENCE` role
        HOME role

android.ext.services.notification  中包含的 NotificationAssistantServices 的 AOSP 实现满足这些要求。
```

#### 3.8.14. 多窗口模式
[C-4-1 和 C-5-1]（2024 年 2 月 5 日预览版）
```
如果设备实现包含一个或多个可折叠的 Android 兼容显示区域，或在多个与 Android 兼容的显示区域之间放置了一个折叠合页，并使此类区域可供应用使用，则：

    [C-4-1] 必须支持多窗口模式。

如果设备实现支持多窗口模式，则：

    [C-5-1] 必须实现正确版本的 Window Manager Extensions API 级别（如 WindowManager 扩展中所述）。

```
### 3.9. 设备管理
[3.9/C-1-1 和 C-1-2]（2024 年 2 月 26 日预览版）
Android 包含一些~~可让注重安全的应用~~[可让设备政策控制器应用](https://source.android.com/docs/devices/admin?hl=zh-cn#how-works)在系统级执行设备管理工作的功能，例如通过 ~~Android Device Administration API~~[Device Policy Manager API](https://developer.android.com/reference/android/app/admin/DevicePolicyManager?hl=zh-cn) 强制执行密码政策或执行远程清除。
```
去除以下规则：

如果设备实现已实现 Android SDK 文档中定义的所有设备管理政策，则：

    [C-1-1] 必须声明 android.software.device_admin。
    [C-1-2] 必须支持设备所有者配置（如第 3.9.1 节和第 3.9.1.1 节中所述）。 
```

#### 3.9.1. 设备配置
##### 3.9.1.1. 设备所有者配置
[C-1-2 至 C-2-3]（2024 年 2 月 26 日预览版）
```
去除以下规则：

[C-1-2] 必须显示一则适当的披露声明（如 AOSP 中所述），并在将某个应用设为设备所有者应用之前征得最终用户明确同意，除非在最终用户通过屏幕与设备互动前，该设备就已以程序化方式配置为零售演示模式。如果设备实现声明了 android.software.device_admin，但还包含专有的设备管理解决方案，并提供了相应机制来向标准 Android DevicePolicyManager API 识别出的标准“设备所有者”通告在其解决方案中配置为“与设备所有者同等”的应用，则：

    [C-2-1] 必须部署相应的流程来验证所通告的特定应用属于合法的企业设备管理解决方案，并且已在专有的解决方案中配置为具备与“设备所有者”同等的权利。

    [C-2-2] 在将 DPC 应用注册为“设备所有者”应用之前，必须先按照 android.app.action.PROVISION_MANAGED_DEVICE 启动的流程显示相同的 AOSP 设备所有者意见征求披露信息。

    [C-2-3] 不得以硬编码方式编写意见征求机制，也不得阻止使用其他的设备所有者应用。

```

##### 3.9.1.2. 受管个人资料配置
[C-1-2]（2024 年 2 月 26 日预览版）
```
去除以下规则：

[C-1-2] 受管理资料配置流程（该流程由 DPC 使用 [android.app.action.PROVISION_MANAGED_PROFILE](http://developer.android.com/reference/android/app/admin/DevicePolicyManager.html?hl=zh-cn#ACTION_PROVISION_MANAGED_PROFILE) 启动或由平台启动）、意见征求屏幕和用户体验必须与 AOSP 实现保持一致。
```
### 3.12. TV 输入框架
[3.12]（2024 年 2 月 26 日预览版）
```
去除以下规则：

[Android TV 输入框架 (TIF)](https://source.android.com/docs/devices/tv?hl=zh-cn) 能够简化向 Android TV 设备传输实时内容的过程。TIF 提供了一个标准 API，用于创建可控制 Android TV 设备的输入模块。

如果设备实现支持 TIF，则：

- [C-1-1] 必须声明平台功能 `android.software.live_tv`。
- [C-1-2] 必须支持所有 TIF API，以便用户在设备上安装和使用利用此类 API 和[基于 TIF 的第三方输入](https://source.android.com/devices/tv?hl=zh-cn#third-party_input_example)服务的应用。
```

### 3.16. 配套设备配对
[C-1-3]（2024 年 2 月 5 日预览版）
- [C-1-3] 必须提供一种方式，让用户能够选择/确认配套设备是否存在以及是否能够正常运作；**<font color="#00b050">并且必须原样使用 AOSP 中实现的消息，不得有任何添加或修改</font>**。

### 3.19. 语言设置
[3.19. 语言设置]（2024 年 2 月 26 日预览版）
```
设备实现：

- [C-0-1] 不得提供任何方式，让用户能够为不支持性别特定翻译的语言选择特定于性别的语言处理方式。如需了解详情，请参阅[语法资源](https://developer.android.com/about/versions/14/features/grammatical-inflection?hl=zh-cn#add-translations)。
```

## 5. 多媒体兼容性
### 5.3. 视频解码
#### 5.3.8. 杜比视界
[C-1-2]（2023 年 12 月 11 日预览版）
- [C-1-2] 必须正确显示杜比视界内容，要么是在设备屏幕上，要么是在**<font color="#00b050">通过标准视频输出端口连接的外部显示屏上</font>**（例如，HDMI）。
### 5.5. 音频播放
#### 5.5.2. 音效
[C-1-4]（2024 年 2 月 5 日预览版）
- [C-1-4] 当效果结果返回到框架音频管道时，必须支持具有浮点输入和输出<font color="#00b050">**的音效。这指的是典型的插入或 Aux 音效，例如均衡器。如果框架音频管道看不到效果结果（例如后处理或分流效果），强烈建议使用等效行为。**</font>

[C-1-5]（2024 年 2 月 5 日预览版）
- [C-1-5] 当效果结果返回到框架音频管道时，必须确保音效支持多个声道，最高可达混音器声道数量（也称为 FCC_LIMIT）。<font color="#00b050">**这指的是典型的插入或 Aux 效果，但不包括会改变声道数量的特效，例如缩混、上混、空间化效果。当框架音频管道看不到效果（例如后期处理或分流效果）时，建议使用等效行为。**</font>

### 5.6. 音频延迟
[头部跟踪延迟定义]（2024 年 2 月 26 日预览版）
- 头部跟踪延迟。<font color="#00b050">**从惯性测量单元 (IMU) 捕获到头部运动到耳机变频器检测到该运动引起的声音变化所经历的时间。**</font>

[C-1-4]（2024 年 2 月 5 日预览版）
- [C-1-4] <font color="#00b050">**根据 AAudioStream_getTimestamp 返回的输入和输出时间戳计算得出的往返延迟时间与 AAUDIO_PERFORMANCE_MODE_NONE 和 AAUDIO_PERFORMANCE_MODE_LOW_LATENCY 的测量往返延迟时间相差不得超过 200 毫秒（针对扬声器、有线耳机和无线耳机）。**</font>

[C-SR-1、C-SR-2、C-SR-4]（2024 年 2 月 5 日预览版）
```
去除以下规则：

如果设备实现声明 `android.hardware.audio.output`，强烈建议它们满足或超出以下要求：
- [C-SR-1] 扬声器数据路径上的冷输出延迟时间不超过 100 毫秒。
- [C-SR-2] 点按与发声间延迟时间不超过 80 毫秒。
- [C-SR-4] 对于根据 `AAudioStream_getTimestamp` 返回的输入和输出时间戳计算得出的往返延迟时间，强烈建议使其与 `AAUDIO_PERFORMANCE_MODE_NONE` 和 `AAUDIO_PERFORMANCE_MODE_LOW_LATENCY` 测量的往返延迟时间相差不超过 30 毫秒（针对扬声器、有线耳机和无线耳机）。
```

[C-SR-5、C-SR-6、C-SR-7]（2024 年 2 月 5 日预览版）
```
去除以下规则：

使用 AAudio 原生音频 API 时，如果设备实现在经过任何初始校准后满足了上述要求，对于在至少一个受支持音频输出设备上的连续输出延迟和冷输出延迟：
- [C-SR-5] 强烈建议通过声明 `android.hardware.audio.low_latency` 功能标志来报告低延迟音频。
- [C-SR-6] 强烈建议通过 AAudio API 满足针对低延迟音频的要求。
- [C-SR-7] 对于从 AAudioStream_getPerformanceMode() 返回 AAUDIO_PERFORMANCE_MODE_LOW_LATENCY 的信息流，强烈建议确保 AAudioStream_getFramesPerBurst() 返回的值小于或等于 android.media.AudioManager.getProperty(String) 针对属性键 AudioManager.PROPERTY_OUTPUT_FRAMES_PER_BUFFER 返回的值。
```

[C-2-1]（2024 年 2 月 5 日预览版）
```
去除以下规则：

如果设备实现未通过 AAudio 原生音频 API 满足针对低延迟音频的要求，则：
[C-2-1] 不得报告对低延迟音频的支持情况。

```

[C-3-1]（2024 年 2 月 5 日预览版）
```
去除以下规则：

[C-3-1] 将 [AudioRecord.getTimestamp](https://developer.android.com/reference/android/media/AudioRecord.html?hl=zh-cn#getTimestamp(android.media.AudioTimestamp,%20int)) 或 `AAudioStream_getTimestamp` 返回的输入时间戳中的误差限制在 +/- 2 毫秒内。“误差”在此是指与正确值的偏差。
```

[C-SR-8、C-SR-11]（2024 年 2 月 5 日预览版）
```
去除以下规则：

如果设备实现包含 android.hardware.microphone，强烈建议它们满足以下针对输入音频的要求：

    [C-SR-8] 麦克风数据路径上的冷输入延迟时间不超过 100 毫秒。
    [C-SR-11] 将 AudioRecord.getTimestamp 或 AAudioStream_getTimestamp 返回的输入时间戳中的误差限制在 +/- 1 毫秒内。

```

[C-SR-12]（2024 年 2 月 26 日预览版）
```
去除以下规则：

如果设备实现声明 android.hardware.audio.output 和 android.hardware.microphone，则：

    [C-SR-12] 强烈建议在至少一条受支持路径上的 5 次测量的平均连续往返延迟不得超过 50 毫秒，平均绝对偏差低于 10 毫秒。

```

[RTL 要求]（2024 年 2 月 5 日预览版）
![[../../resource/Pasted image 20241127152714.png]]

[TTL 要求]（2024 年 2 月 5 日预览版）
![[../../resource/Pasted image 20241127152732.png]]

[C-4-1]（2024 年 2 月 26 日预览版）
```
如果设备实现支持带头部跟踪功能的 spatial audio，并声明 PackageManager.FEATURE_AUDIO_SPATIAL_HEADTRACKING_LOW_LATENCY 标志，则：

    [C-4-1] 头部跟踪到音频更新的最大延迟必须为 300 毫秒。
```

### 5.10. 专业音频
[C-1-8、C-SR-1、C-SR-2、C-SR-3]（2024 年 2 月 5 日预览版）
```
去除以下规则：

    [C-1-8] 在扬声器到麦克风数据路径上的至少 5 次测量中，平均点按与发声间延迟时间不得超过 80 毫秒。
    [C-SR-1] 强烈建议满足第 5.6 节 - 音频延迟中所定义的延迟要求，即在扬声器到麦克风路径上的 5 次测量的延迟不得超过 20 毫秒，平均绝对偏差低于 5 毫秒。
    [C-SR-2] 强烈建议在 MMAP 路径上使用 AAudio 原生音频来满足对连续往返音频延迟、冷输入延迟和冷输出延迟的专业音频要求以及 USB 音频要求。
    [C-SR-3] 强烈建议当音频在播放并且 CPU 负载有变化时，提供水平一致的 CPU 性能。应使用 Android 应用 SynthMark 对此进行测试。SynthMark 会使用在测量系统性能的模拟音频框架上运行的软件合成器。请参阅 SynthMark 文档，了解基准说明。SynthMark 应用需要使用“自动测试”选项运行并获得以下结果：
        voicemark.90 >= 32 个语音
        latencymark.fixed.little <= 15 毫秒
        latencymark.dynamic.little <= 50 毫秒
    应最大限度地降低音频时钟相对于标准时间的不准确性和偏差。
    应最大限度地降低音频时钟相对于 CPU CLOCK_MONOTONIC 的偏差（当两者皆处于活动状态时）。
    应最大限度地缩短在设备内置变频器上的音频延迟。
    应最大限度地缩短在 USB 数字音频路径上的音频延迟。
    应记录在所有路径上的音频延迟时间测量结果。
    应最大限度地降低音频缓冲完成回调输入时间内的抖动，因为此类抖动会影响全 CPU 带宽中可供回调使用的百分比。
    在正常使用情况下（符合报告的延迟），不应出现音频干扰。
    声道间延迟时间差应为零。
    采用各种传输方式时，都应最大限度地缩短 MIDI 平均延迟。
    采用各种传输方式时，都应最大限度地降低在有负载状态下的 MIDI 延迟变化（抖动）。
    采用各种传输方式时，都应提供准确的 MIDI 时间戳。
    应最大限度地降低在设备内置变频器上的音频信号噪声，包括刚完成冷启动后一段时间内的噪声。
    相应端点输入侧和输出侧（当两者皆处于活动状态时）之间的音频时钟差应为零。相应端点的示例包括设备上的麦克风和扬声器，或音频插孔输入端和输出端。
    应在同一线程上处理相应端点输入侧和输出侧（当两者皆处于活动状态时）的音频缓冲完成回调，并在从输入回调返回后立即进入输出回调。或者，如果在同一线程上处理回调不可行，则应在进入输入回调后很快进入输出回调，以便应用在输入侧和输出侧拥有一致的时间。
    应最大限度地减小相应端点输入侧和输出侧 HAL 音频缓冲之间的相位差。
    应最大限度地缩短触摸延迟。
    应最大限度地降低在有负载状态下的轻触延迟时间变化（抖动）。
```

[C-SR-4]（2024 年 2 月 5 日预览版）
```
去除以下规则：

如果设备实现满足上述所有要求，则：
    [C-SR-4] 强烈建议通过 android.content.pm.PackageManager 类报告对 android.hardware.audio.pro 功能的支持情况。

```

[C-2-1]（2024 年 2 月 5 日预览版）
```
去除以下规则：

[C-2-1] 如第 5.6 节 - 音频延迟中所定义，在使用音频环回适配器的音频耳机插孔路径上的 5 次测量中，平均连续往返音频延迟时间不得超过 20 毫秒，平均绝对偏差低于 5 毫秒。
```

[C-SR-5]（2024 年 2 月 5 日预览版）
- [C-SR 2-5 2] <font color="#00b050">**必须遵循**</font>有线音频耳机规范 (v1.1) 的移动设备（耳机插孔）规范一节中的规定。

[C-3-2、C-SR-6、C-SR-7]（2024 年 2 月 5 日预览版）
```
去除以下规则：

    [C-3-2] 使用 USB 音频类时，在 USB 主机模式端口上的 5 次测量的平均连续往返音频延迟不得超过 25 毫秒，平均绝对偏差低于 5 毫秒。（可以使用 USB-3.5 毫米适配器和音频环回适配器进行测量，也可以使用配备用于连接输入端和输出端的跳线的 USB 音频接口进行测量）。
    [C-SR-6] 与同样支持这些要求的 USB 音频外围设备结合使用时，强烈建议支持每个方向最多 8 个声道的同时 I/O、96 kHz 采样率和 24 位或 32 位深。
    [C-SR-7] 强烈建议在 MMAP 路径上使用 AAudio 原生音频 API 来满足这组要求。

```

[HDMI 端口要求]（2024 年 2 月 5 日预览版）
```
去除以下规则：

如果设备实现包含 HDMI 端口，则：
    应在至少一种配置中支持频率为 192 kHz、位深为 20 或 24 的八声道立体声输出，而不丢失位深或重新采样。
```

## 6. 开发者工具和选项兼容性
### 6.1. 开发者工具
[C-0-2]（2024 年 2 月 5 日预览版）
- [C-0-2] 必须支持 adb（如 Android SDK 中所述）和 AOSP 中提供的 shell 命令（可供应用开发者使用，包括 dumpsys、cmd stats 和 **<font color="#2DC26B">Simpleperf</font>**）。

[C-0-10]（2023 年 12 月 11 日预览版）
- [C-0-10] 记录时不得有任何遗漏，并使以下事件可供 cmd stats shell 命令和 StatsManager 系统 API 类访问和使用。 
- ActivityForegroundStateChanged
- AnomalyDetected
- AppBreadcrumbReported
- AppCrashOccurred
- AppStartOccurred
- BatteryLevelChanged
- BatterySaverModeStateChanged
- BleScanResultReceived
- BleScanStateChanged
- ChargingStateChanged
- DeviceIdleModeStateChanged
- ForegroundServiceStateChanged
- GpsScanStateChanged
- **<font color="#2DC26B">InputDeviceUsageReported</font>**
- JobStateChanged
- **<font color="#2DC26B">KeyboardConfigured</font>**
- **<font color="#2DC26B">KeyboardSystemsEventReported</font>**
- PluggedStateChanged
- ScheduledJobStateChanged
- ScreenStateChanged
- SyncStateChanged
- SystemElapsedRealtime
- **<font color="#2DC26B">TouchpadUsage</font>**
- UidProcessStateChanged
- WakelockStateChanged
- WakeupAlarmOccurred
- WifiLockStateChanged
- WifiMulticastLockStateChanged
- WifiScanStateChanged

## 7. 硬件兼容性
### 7.1. 显示和图形
#### 7.1.1. 屏幕配置
##### 7.1.1.1. 屏幕尺寸和形状
[C-4-1]（2024 年 2 月 5 日预览版）
```
去除以下规则

如果设备实现包含一个或多个可折叠的 Android 兼容显示区域，或在多个与 Android 兼容的显示面板区域之间放置了一个折叠合页，并使此类显示区域可供应用使用，则：
    [C-4-1] 必须实现正确版本的 Window Manager Extensions API 级别（如 WindowManager 扩展中所述）。
```

#### 7.1.4. 2D 和 3D 图形加速
##### 7.1.4.1. OpenGL ES
[C-1-1]（2023 年 12 月 11 日预览版）
- [C-1-1] 必须~~同时~~支持 OpenGL ES 1.1、~~和~~2.0、**<font color="#2DC26B">3.0 和 3.1</font>**，如 [Android SDK 文档](https://developer.android.com/guide/topics/graphics/opengl.html?hl=zh-cn)中所详述。

[C-SR-1]（2023 年 12 月 11 日预览版）
- ~~[C-SR-1] 强烈建议支持 OpenGL ES 3.1。~~

##### 7.1.4.2. Vulkan
[C-SR-8 和 C-1-14]（2023 年 12 月 11 日预览版）
```
如果设备实现支持 Vulkan，则：

    [C-SR-8] 强烈建议不要修改 Vulkan 加载程序。
    [C-1-14] 不得枚举类型为“KHR”“GOOGLE”或“ANDROID”的 Vulkan 设备扩展，除非这些扩展包含在 android.software.vulkan.deqp.level 功能标志中。

注意：在 Android 16 中，C-SR-8 将成为必须满足的要求。
```

### 7.3. 传感器
#### 7.3.10. 生物识别传感器
[C-4-4]（2024 年 4 月 8 日预览版）
```
[C-4-4] 必须允许应用使用 PromptContentView 内容显示格式向 BiometricPrompt 添加自定义内容。不得扩展内容显示格式来允许 BiometricPrompt API 中尚无的图像、链接、互动式内容或其他形式的媒体。可以进行不会改变、遮挡或截断此类内容的样式调整（例如更改位置、内边距、外边距和排版）。
```

[C-1-1]（2023 年 12 月 11 日预览版）
- [C-1-1] 错误接受率必须低于 ~~0.002%~~<font color="#2DC26B"> 0.001%。</font>

[C-1-11]（2023 年 12 月 11 日预览版）
```
去除以下规则：

[C-1-11] 欺骗和冒名攻击的接受率不得高于 30%；并且 (1) 针对 A 级演示攻击手段 (PAI) 类型的欺骗和冒名攻击的接受率不得高于 30%；(2) 针对 B 级 PAI 类型的欺骗和冒名攻击的接受率不得高于 40%（此值由 Android 生物识别测试协议衡量得出）。
```

[C-1-5]（2023 年 12 月 11 日预览版）
- [C-1-5] 当移除某个用户的账号（包括通过恢复出厂设置）时，<font color="#2DC26B">或者移除所建议的主要身份验证方法（例如 PIN 码、图案、密码）时</font>，必须完全删除该用户所有可识别的生物识别数据。

[C-1-7]（2024 年 4 月 8 日预览版）
- [C-1-7] 必须以不低于每 24 小时一次的频率让用户进行建议的主要身份验证（例如 PIN 码、图案、密码）。 ~~注意：如果是发布时搭载 Android 9 或更低版本而后升级的设备，必须以不低于每 72 小时一次的频率让用户进行建议的主要身份验证（例如PIN 码、图案、密码）。~~

[C-1-8]（2023 年 12 月 11 日预览版）
- [C-1-8] 必须在执行以下操作之一后对用户进行建议的主要身份验证（例如 PIN 码、图案、密码）或第 3 类（强）生物识别：
- - 4 小时空闲超时期限，或
-  -尝试生物识别身份验证失败 3 次。
-  -空闲超时期限和失败的身份验证计数将在每次成功确认设备凭据后重置。~~注意：发布时搭载 Android 9 或更低版本而后升级的设备可以不遵守 C-1-8 要求。~~

[C-1-14]（2023 年 12 月 11 日预览版）
- [~~C-1-12] **每种演示攻击手段 (PAI) 类型**的欺骗和冒名攻击的接受率不得高于 40%（此值由 [Android 生物识别测试协议](https://source.android.com/docs/security/features/biometric/measure?hl=zh-cn)衡量得出）。~~

[C-1-13]（2023 年 12 月 11 日预览版）
- [~~C-SR-13~~C-1-13]~~强烈建议~~**每种演示攻击手段 (PAI) 类型**<font color="#2DC26B">必须</font>具有不高于 30%（此值由 [Android 生物识别测试协议](https://source.android.com/docs/security/features/biometric/measure?hl=zh-cn)衡量得出）的欺骗和冒名攻击接受率。

[C-1-14]（2024 年 4 月 8 日预览版）
- [C-1-14] <font color="#2DC26B">必须确保在设备上测得的错误拒绝率低于 10%。</font>

[C-1-15]（2023 年 12 月 11 日预览版）
- [C-1-15] <font color="#2DC26B">必须允许用户移除一项或多项生物识别注册信息。</font>

[C-2-2]（2023 年 12 月 11 日预览版）
- ~~[C-2-2] 欺骗和冒名攻击的接受率不得高于 20%；并且 (1) 针对 A 级演示攻击手段 (PAI) 类型的欺骗和冒名攻击的接受率不得高于 20%；(2) 针对 B 级 PAI 类型的欺骗和冒名攻击的接受率不得高于 30%（此值由 Android 生物识别测试协议衡量得出）。~~

[C-2-10]（2023 年 12 月 11 日预览版）
- [~~C-SR-15~~C-2-10]~~强烈建议~~**每种演示攻击手段 (PAI) 类型**<font color="#2DC26B">必须</font>具有不高于 20%（此值由 [Android 生物识别测试协议](https://source.android.com/docs/security/features/biometric/measure?hl=zh-cn)衡量得出）的欺骗和冒名攻击接受率。

[C-3-3]（2023 年 12 月 11 日预览版）
- ~~[C-3-3] 欺骗和冒名攻击的接受率不得高于 7%；并且 (1) 针对 A 级演示攻击手段 (PAI) 类型的欺骗和冒名攻击的接受率不得高于 7%；(2) 针对 B 级 PAI 类型的欺骗和冒名攻击的接受率不得高于 20%（此值由 Android 生物识别测试协议衡量得出）。~~

[C-3-7]（2023 年 12 月 11 日预览版）
- [~~C-SR-16~~C-3-7]~~强烈建议~~**每种演示攻击手段 (PAI) 类型**<font color="#2DC26B">必须</font>具有不高于 7%（此值由 [Android 生物识别测试协议](https://source.android.com/docs/security/features/biometric/measure?hl=zh-cn)衡量得出）的欺骗和冒名攻击接受率。

### 7.4. 数据连接
#### 7.4.2. IEEE 802.11 (Wi-Fi)
[C-1-4]（2023 年 12 月 11 日预览版）
- ~~[C-1-4] 必须支持多播 DNS (mDNS)，并且不得在操作过程中的任何时候滤除 mDNS 数据包（224.0.0.251 或 ff02::fb），包括在屏幕未处于活动状态时；除非丢弃或滤除这些数据包是为了保持在目标市场适用法规所要求的能耗范围内，必须如此。~~
- [C-1-4] <font color="#2DC26B">必须支持 mDNS，并且不得在操作过程中的任何时间过滤 mDNS 数据包（224.0.0.251 或 ff02::fb），包括屏幕未处于活动状态时，除非不持有多播锁定且数据包由 APF 过滤。数据包无需满足应用当前通过 NsdManager API 请求的任何 mDNS 操作的要求。不过，如果有必要这样做才能使功耗保持在适用于目标市场的监管要求所规定的功耗范围内，设备可以过滤 mDNS 数据包。</font>

## 9. 安全模型兼容性
### 9.1. 权限
[C-0-16]（2024 年 2 月 5 日预览版） 
```
    [C-0-16] protectionLevel 为 PROTECTION_SIGNATURE 的权限只能授予：
        预安装在系统映像上的应用（以及 APEX 文件）。
        已列入许可名单且具有许可权限的应用（如果它们未包含在系统映像中）。

    AOSP 实现通过以下方式来满足此要求：从 etc/permissions/ 路径下的文件中读取为各个应用列入许可名单的权限，并遵从此类权限。

```

### 9.7. 安全功能
[C-SR-17 至 C-SR-20] [已重新编号]（2024 年 4 月 8 日预览版）
```
如果设备声明了 android.hardware.telephony，支持无线装置功能 CAPABILITY_USES_ALLOWED_NETWORK_TYPES_BITMASK，并且包含支持 2G 连接的移动网络调制解调器，则设备实现：

    [C-SR-17] 强烈建议提供一种方式，让用户能够停用和启用 2G。
    [C-SR-18] 强烈建议不覆盖方便用户通过任何其他设备实体停用和启用 2G 的方式，除了设备管理员使用 UserManager.DISALLOW_CELLULAR_2G 停用和启用 2G 之外。
    [C-SR-19] 强烈建议出于 ALLOWED_NETWORK_TYPES_REASON_ENABLE_2G 原因调用 TelephonyManager.setAllowedNetworkTypesForReason 以满足此要求。
    [C-SR-20] 强烈建议通过调用 TelephonyManager.getSupportedRadioAccessFamily 来确定移动网络调制解调器是否支持 2G。如需了解详情，请参阅停用 2G。

注意：在 Android W（AOSP 实验版）中，强烈建议满足的要求（C-SR-17 至 C-SR-20）将成为必须满足的要求。
```

### 9.8. 隐私设置
#### 9.8.2. 录制
[C-0-5 和 C-0-6]（2024 年 4 月 8 日预览版）
```
设备实现：

- [C-0-5] 不得更改应用的 [`FLAG_SECURE`](https://developer.android.com/reference/android/view/WindowManager.LayoutParams?hl=zh-cn#FLAG_SECURE) 设置。
- [C-0-6] 必须提供一种方式，让用户能够通过“开发者选项”菜单关闭敏感通知保护功能的屏幕录制。
```


[C-3-1 至 C-3-3]（2024 年 4 月 8 日预览版）
```
如果录屏功能处于活跃状态，且不是从系统界面或 OEM bug 报告应用中启动的，则设备通知实现：

    [C-3-1] 必须仅在通知的可见性为 VISIBILITY_PUBLIC 时显示通知内容，或者在通知内容可见的所有 Surface（包括锁定的屏幕、浮动通知、通知栏、消息气泡和启动器圆点）上显示已隐去敏感信息的通知内容（仅限应用图标和应用名称），除非满足以下至少一项：
        共享部分屏幕。
        通知内容不会泄露任何个人数据或敏感用户数据，例如当通知是由录制屏幕的应用发布的前台服务时，或当通知来自 Android 系统时。

    [C-3-2] 如果应用发出了包含检测到的动态密码的通知，则必须调用 WindowState.setSecureLocked(true) 隐藏隐藏这些应用的窗口。

    [C-3-3] 当 CONTENT_SENSITIVITY_SENSITIVE 可见时，或当框架启发法确定该视图包含任何下述类型的敏感数据时，必须隐藏敏感视图或应用窗口：
        View.AUTOFILL_HINT_USERNAME
        View.AUTOFILL_HINT_PASSWORD
        输入类型 TYPE_TEXT_VARIATION_PASSWORD
        输入类型 TYPE_TEXT_VARIATION_WEB_PASSWORD
        输入类型 TYPE_NUMBER_VARIATION_PASSWORD
        输入类型 TYPE_TEXT_VARIATION_VISIBLE_PASSWORD

```

#### 9.8.14. Credential Manager
- ~~在 Android 14 中已移除。~~.
- <font color="#2DC26B">设备实现必须声明支持 `android.software.credentials`</font>
- <font color="#2DC26B">必须遵从 android.settings.CREDENTIAL_PROVIDER intent，以允许为 Credential Manager 选择首选提供程序。系统将针对自动填充服务启用此提供程序，并且此提供程序也将成为通过 Credential Manager 保存新凭据的默认位置。</font>
- <font color="#2DC26B">必须支持至少 2 个并发凭据提供程序，并在“设置”应用中提供一种方式，让用户能够启用或停用这些提供程序。</font>


#### 9.8.16. 连续的音频和摄像头数据
[9.8.16]（2024 年 2 月 26 日预览版）
- ~~除了第 9.8.2 节“录制”、第 9.8.6 节“操作系统级数据和环境数据”以及第 9.8.15 节“沙盒化 API 实现”中列出的要求之外，如果实现会使用通过 AudioRecord、SoundTrigger 或其他音频 API 在后台（连续）获取的音频数据或者通过 CameraManager 或其他相机 API 在后台（连续）获取的相机数据，则：~~
- <font color="#00b050">如果设备实现会捕获第 9.8.2 或第 9.8.6 节中所述的任何数据，并且此类实现会使用通过 AudioRecord、SoundTrigger 或其他 Audio API 在后台（连续）获取的音频数据，或者通过 CameraManager 或其他 Camera API 在后台（连续）获取的相机数据，则：</font>

[C-1-1]（2024 年 2 月 26 日预览版）
- ~~如果相机数据是由远程穿戴式设备提供的，并在脱离 Android 操作系统、沙盒化实现或由 WearableSensingManager 构建的沙盒化功能情况下，以非加密的形式处理，则：~~
- <font color="#00b050">如果设备实现从远程穿戴式设备接收摄像头或麦克风数据，并且这些数据是在 Android OS、沙盒化实现或由 WearableSensingManager 构建的沙盒化功能之外以未加密形式访问的，则：[C-1-1] 必须指示远程穿戴式设备在相应位置显示额外的指示器。</font>

### 9.10. 设备完整性
[C-1-12 至 C-1-14]（2024 年 2 月 26 日预览版）
- ~~[C-SR-1] 如果设备中有多个离散芯片（例如无线装置、专门的图像处理器），强烈建议其中每个芯片的启动进程在启动时验证每个阶段。~~
- <font color="#00b050">[C-1-12] 如果设备中有多个离散芯片（例如无线装置、专用图片处理器），则必须在启动时的每个阶段验证每个芯片的启动进程。</font>
- <font color="#00b050">[C-1-14] 对于系统配置中列为 require-strict-signature 的许可名单软件包，在每次启动时必须验证签名至少 1 次。</font>

[关于 C-1-8 至 C-1-13 的说明]（2024 年 2 月 26 日预览版）
- ~~如果设备实现已在不支持 C-1-8 至 C-1-11 的情况下搭载早期 Android 版本，且无法通过系统软件更新满足上述要求，则可以不遵守这些要求。~~

 [C-SR-4]、[C-3-1]、[C-3-2] 和 [C-3-3]（2024 年 2 月 5 日预览版）
- ~~[C-SR-4] 强烈建议支持 [Android Protected Confirmation API](https://developer.android.com/about/versions/pie/android-9.0?hl=zh-cn#security)。如果设备实现支持 Android Protected Confirmation API，则~~
- ~~[C-3-1] 必须针对 [`ConfirmationPrompt.isSupported()`](https://developer.android.com/reference/android/security/ConfirmationPrompt.html?hl=zh-cn#isSupported(android.content.Context)) API 报告 `true`。~~
- ~~[C-3-2] 必须确保 Android OS 中运行的代码（包括其内核和恶意内容等）在没有用户互动的情况下无法生成积极回应。~~
- ~~[C-3-3] 即使 Android OS（包括其内核）遭到入侵，也必须确保用户能够审核和批准提示消息。~~

### 9.11. 密钥和凭据
[C-1-4]（2023 年 12 月 11 日预览版）
- [C-1-4] 如果认证签名密钥受安全硬件保护，并且签名是在安全硬件中进行，必须支持密钥认证。认证签名密钥必须~~在足够多的设备之间共享，以防止此类密钥~~被<font color="#00b050">阻止用作永久设备标识符。</font>
![[../../resource/Pasted image 20241127161826.png]]
#### 9.11.1. 安全锁定屏幕、身份验证和虚拟设备
[C-10-6]（2024 年 2 月 5 日预览版）
- [C-10-6] 当 `DevicePolicyManager.setNearbyAppStreamingPolicy` 指明时，必须停用~~通过 `VirtualDeviceManager` 创建关联的输入事件~~<font color="#00b050">应用串流功能</font>。

[C-10-7]（2024 年 2 月 5 日预览版）
<font color="#00b050">- [C-10-7] 必须满足以下条件之一：</font>
<font color="#00b050">- 停用剪贴板</font>
<font color="#00b050">- 为支持剪贴板的每台设备启用单独的剪贴板</font>
- ~~[C-10-7] 必须为每台虚拟设备专门使用单独的剪贴板（或为虚拟设备停用剪贴板）~~

[C-10-12] [已移除]（2024 年 2 月 5 日预览版）
- ~~[C-10-12] 必须限制从虚拟设备发起的 intent 仅在同一虚拟设备上显示~~
- <font color="#00b050">[C-10-12] 此要求已从 Android 15（AOSP 实验版）中移除。</font>

[C-10-14 和 C-10-15]（2024 年 2 月 5 日预览版）
- <font color="#00b050">[C-10-14] 必须提供一种方式，让用户能够先启用在设备之间共享剪贴板数据的功能，然后在实体设备和虚拟设备之间共享剪贴板数据（如果设备实现了共享剪贴板）。</font>
- <font color="#00b050">[C-10-15] 必须在跨设备访问剪贴板数据时显示通知，并且必须使内容在从初始共享时间算起一分钟后无法再访问。</font>

#### 9.11.2. StrongBox
[C-1-10]（2023 年 12 月 11 日预览版）
- [C-1-10] 包含的硬件必须经过安全 IC 保护配置文件 [BSI-CC-PP-0084-2014](https://www.commoncriteriaportal.org/files/ppfiles/pp0084b_pdf.pdf) <font color="#00b050">或 [BSI-CC-PP-0117-2022](https://www.commoncriteriaportal.org/files/ppfiles/pp0117a_pdf.pdf) 认证</font>，或经过由国家认可的测试实验室的评估，以及根据[Common Criteria Application of Attack Potential to Smartcards](https://www.commoncriteriaportal.org/files/supdocs/CCDB-2013-05-002.pdf) 进行的高攻击性潜在漏洞评估。

### 9.17. Android 虚拟化框架
[9.17]（2024 年 2 月 26 日预览版）
```
借助 Android 虚拟化框架 (AVF) API (`android.system.virtualmachine.*`)，应用可以创建设备端虚拟机 (VM)，以便以载荷的形式加载和运行原生二进制文件。

如果设备实现将 `FEATURE_VIRTUALIZATION_FRAMEWORK` 设置为 `true`，则：

- [C-1-6] 必须确保 `android.system.virtualmachine.VirtualMachineManager.getCapabilities()` 至少返回以下项之一：
    - `CAPABILITY_PROTECTED_VM`
    - `CAPABILITY_NON_PROTECTED_VM`
```

### 9.18. 受限设置
[9.18]（2023 年 12 月 11 日预览版）
```
设备实现：

[C-0-1] 必须实现并启用对“受限设置”模式的支持。 受限设置适用于已旁加载且声明需要某些“受限权限”的所有应用。“受限权限”不一定是权限，而是被视为对安全性敏感的角色和其他功能。具体而言，受限设置的范围内“权限”包括：
- 无障碍功能
- 通知监听器
- 默认应用（主屏幕、电话、短信）
- 属于设备管理应用
- 显示在其他应用的上层
- 使用情况访问权限
- 媒体投屏
- 短信
- 呼叫

如果应用是通过下载的文件或[本地文件](https://developer.android.com/reference/android/content/pm/PackageInstaller?hl=zh-cn#PACKAGE_SOURCE_DOWNLOADED_FILE)安装的，则会被标识为“旁加载”。
```