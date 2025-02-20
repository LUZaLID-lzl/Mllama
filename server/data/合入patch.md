1：压缩包解压在**rs10/vnd/alps-release-s0.mp1.rc-tb/vendor/mobiiot/etc/sepolicy/hikrobotics/vendor**目录下

需要自己创建文件夹

![image-20240903182306828](/home/liziluo/LUZaLID/TyporaPicture/image-20240903182306828.png)

2：修改**rs10/vnd/alps-release-s0.mp1.rc-tb/vendor/mobiiot/vendor_boardconfig.mk**

添加一行：BOARD_SEPOLICY_DIRS += vendor/mobiiot/etc/sepolicy/hikrobotics/vendor

![image-20240903182420543](/home/liziluo/LUZaLID/TyporaPicture/image-20240903182420543.png)