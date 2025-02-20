## README

当前问题：A13通过OTA降级到A11后，tee相关的属性值变化(eg:vendor.trustkernel.productionline.state 从 ready变为none)

当前机器状态：机器已经写入google key，且为A13的userdebug版本，文件管理器内放置了两个OTA包（分别为升级包和降级包）

测试步骤：进入setting--Datalogic settings--Systemupdate--Local update，选择降级包进行版本降级，降级后查看属性值状态

