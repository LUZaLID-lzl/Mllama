
#### Recovery模式下OTA升级,adb不可用
vnd ： bootable/recovery/recovery_main.cpp
```java
static bool IsRoDebuggable() {
  //[261777]recovery mod can not ota
  //return android::base::GetBoolProperty("ro.debuggable", false);
  return true;
}
```
