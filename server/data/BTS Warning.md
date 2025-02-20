仅针对过GMS项目的预制应用

------
#bts #gms
**描述信息**：
Blocked app /system/apex/com.android.devicelock.apex  
This build contains pre-installed "com.android.devicelock" at /system/apex/com.android.devicelock.apex which has been signed by an example private key that's available publicly in AOSP. Find more information at [https://docs.partner.android.com/security/advisories/2023/advisory-2023-11](https://docs.partner.android.com/security/advisories/2023/advisory-2023-11) If you believe this finding is incorrect please reach out  to your TAM and provide details that help us to validate inaccuracies and improve detection.

**解决方案**：
```
更换com.android.devicelock.pem以及com.android.devicelock.avbpubkey替换成内部签名
```
-----
#bts #gms
**描述信息**：
mbw/app/NewFactoryDevelopX/NewFactoryDevelopX.apk:android.permission.CAMERA
camera为敏感权限需要向google申请白名单
否则使用以下接口会提示warning：
- android/hardware/Camera;->takePicture
- android/hardware/camera2/CameraCaptureSession;->capture 
- android/hardware/camera2/CameraDevice;->createCaptureRequest
- android/hardware/camera2/CameraManager;->openCamera

**解决方案**：
```
工模等内部测试应用通过Intent调用系统camera：
private static final int REQUEST_IMAGE_CAPTURE = 1;

Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
intent.putExtra("android.intent.extra.USE_FRONT_CAMERA", true);//前置
startActivityForResult(intent, REQUEST_IMAGE_CAPTURE);
```
-----
#bts #gms
**描述信息**：
The app declares the following sensitive permissions which need to be reviewed and allowlisted: android.permission.ACCESS_FINE_LOCATION
The app declares the following sensitive permissions which need to be reviewed and allowlisted: android.permission.ACCESS_COARSE_LOCATION
定位为敏感权限需要向google申请白名单
否则使用以下接口会提示warning：
- GnssStatus.Callback gnssStatusCallback
- LocationListener mLocListener;

**解决方案**：
```
在内部服务中进行卫星定位，获取到卫星数据后返回给工模
```
-----
#bts #gms
**描述信息**：
mbw/app/NewFactoryDevelopX/NewFactoryDevelopX.apk:android.permission.READ_PHONE_STATE | android.permission.READ_PRIVILEGED_PHONE_STATE
android/os/Build;->getSerial
否则使用以下接口会提示warning：
- Build.getSerial()

**解决方案**：
```
读取属性值
```
