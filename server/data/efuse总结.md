# Efuse相关问题总结

### 1：KEY的产生

生成一对root key(包括private和public key),并用pem_to_der.py脚本来转换key格式

**1.路径：vendor/mediatek/proprietary/scripts/sign-image_v2/der_extractor**


```
openssl genrsa -out root_prvk.pem 2048
openssl rsa -in root_prvk.pem -pubout > root_pubk.pem
```

**2.利用pem_to_der.py 转换key格式,生成root_prvk.der**

```
python pem_to_der.py root_prvk.pem root_prvk.der
python pem_to_der.py root_pubk.pem root_pubk.der
```

**3.用上面方式生成img_prvk.pem,后续用来签名和校验img**

路径：vendor/mediatek/proprietary/scripts/sign-image_v2/der_extractor

```
openssl genrsa -out img_prvk.pem 2048
python pem_to_der.py img_prvk.pem img_prvk.der
```

生成oemkey.h,并用pem_to_der.py脚本来转换key格式

**4.用der_extractor将root key(root_pubk.der)导出生成oemkey.h**

```
chmod a+x der_extractor
./der_extractor root_pubk.der oemkey.h ANDROID_SBC
```

**5.将生成的oemkey.h文件放在下面几个路径:**

```
[PL]vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/xet571/inc/oemkey.h
[LK]vendor/mediatek/proprietary/bootable/bootloader/lk/target/xet571/inc/oemkey.h
[DA]SP_Flash_Tool(Official)_ALPS/FLASHLIB_DA_EXE_v7.1824.00.000/bin/Customization_Kit_buildspec/Raphael-da/custom/MT6771/oemkey.h
```

**6.生成dakey.h**

功能: dakey.h中包含的DA_PL publuc_key用于preloader校验DA_PL.bin,故在签名 DA_PL.bin时需要拿这把key对应的private key对DA_PL.bin做签名。

可以用“key的产生”中的方法重新生成一个key，也可以用root key

```
./der_extractor root_pubk.der dakey.h ANDROID_SBC
```

生成的dekey.h, 需要打开dekey.h然后把"OEM"全部替换为"DA",否则编译会报错

**7.把dekey.h放到下面路径**

```
[PL]vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/xet571/inc/dakey.h
```



------

### 2：开启SECURE BOOT

**1.修改以下宏配置如下：**

路径：vendor/mediate/proprietary/bootable/bootloader/preloader/custom/xet571/xet571.mk

```
MTK_SECURITY_SW_SUPPORT=yes
MTK_SEC_BOOT=ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP
MTK_SEC_USBDL=ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP
```

注意：有些项目secure boot是默认开启的（条件是刷入efuse成功后生效）

说明： 情况一：如果是hw root of trust,需要烧efuse的，会在efuse烧成功后开启security boot和 security download

```
MTK_SEC_BOOT=ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP
MTK_SEC_USBDL=ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP
```

情况二：如果是sw root of trust,也就是不烧入efuse,但是需要强制实现security boot 和 security download,用软件方式强制打开image校验，可以在未烧写efuse前验证部分校验流 程，请按如下配置：

```
MTK_SEC_BOOT=ATTR_SBOOT_ENABLE
MTK_SEC_USBDL=ATTR_SUSBDL_ENABLE
```

注意：以上二者仅仅是在未刷efuse情况下有所区别，正常流程需刷efuse的配置可二选一

**2.路径：vendor/mediate/proprietary/bootable/bootloader/lk/project/xet571.mk**

```
MTK_SECURITY_SW_SUPPORT=yes
```

**3.下面两个宏是可选的(一般不要改)，如果需要支持fastboot的command,请把如下 宏打开**

```
MTK_SEC_FASTBOOT_UNLOCK_SUPPORT=no
//同时,如果需要实现fastboot unlock时需要key的校验,如下宏也需要同时打开
MTK_SEC_FASTBOOT_UNLOCK_KEY_SUPPORT=no
```

注意: 默认fastboot unlock key校验算法较为简单，仅作为参考，如果配置为yes打 开的话，则厂商务必做客制化unlock的验证流程，否则会有通过fastboot刷机的风险 ！！！！

**4.在对应的路径下添加如下宏配置**

路径： 
32 bit project/eng load
<kernel path>/arch/arm/configs/<project>_debug_defconfig
<kernel path>/arch/arm/configs/<project>_defconfig
64 bit project/eng load
<kernel path>/arch/arm64/configs/<project>_debug_defconfig
<kernel path>/arch/arm64/configs/<project>_defconfig

```
CONFIG_MTK_SECURITY_SW_SUPPORT=y
```



------

### 3：软件编译

根据项目实际情况进行编译

```
source build/envsetup.sh
lunch xet571-user
make -j8 2>&1 | tee build.log
```



------

### 4：Preloader签名

**1.Preloader签名 : Build cert_chain 格式的preloader及在build过程中sign preloader 的配置**

将生成的root key (img_prvk.pem与root_prvk.pem)拷贝到下面的路径：

vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/xet571/security/chip_config/s/key

![](/home/liziluo/LUZaLID/TyporaPicture/efuse总结/1.png)

chip_config/s/gfh/pl_gfh_config_cert_chain.ini中配置正确的flash_dev类型 注意：里面的version等信息不可随意更改！

![](/home/liziluo/LUZaLID/TyporaPicture/efuse总结/2.png)

**2.Build preloader**



------

### 5：除preloader外其他img签名

**1.产生cert1和cert2 key**

cert1_key_path=./vendor/mediatek/proprietary/scripts/signimage_v2/der_extractor/root_prvk.pem

cert2_key_path=./vendor/mediatek/proprietary/scripts/signimage_v2/der_extractor/img_prvk.pem

**2.在vendor/mediatek/proprietary/scripts/sign-image_v2目录下执行如下指令（以下为一条完整指令）**

```
python vendor/mediatek/proprietary/scripts/sign-image_v2/img_key_deploy.py
mt6765 dl36 cert1_key_path=./vendor/mediatek/proprietary/scripts/signimage_v2/der_extractor/root_prvk.pem
cert2_key_path=./vendor/mediatek/proprietary/scripts/signimage_v2/der_extractor/img_prvk.pem root_key_padding=pss | tee
img_key_deploy.log
```

不同项目需更改平台(mt6771)以及项目名(xet571)

注意：执行完img_key_deploy.py后,请检查env.cfg中配置的两个目录的文件是否更新

```
../../custom/mt6771/security/cert_config/cert1
../../custom/mt6771/security/cert_config/cert2_key
```

**3.产生签名image**

Cert1和cert2 key正确产生后，就可以执行签名脚本，产生xx-verified.bin,xxverified.img了

执行如下命令签名所有img:

根目录下执行：./vendor/mediatek/proprietary/scripts/sign-image/sign_image.sh

支持单独签名一个img可以用下面指令

python sign_flow.py -env_cfg env.cfg -target lk.img mt6771 xet571 | tee sign_flow.log

用-target指定某个img

------

### 6：Sign DA

**1.编译DA**

确保前面生成的**oemkey.h**放到如下路径 

[DA编译]/Customization_Kit_buildspec/Raphaelda/custom/MT6771/oemkey.h

Window电脑按如下配置好gcc和make 

(1).安装make-3.81.exe

(2).将make加入到环境变量 C:\Program Files (x86)\GnuWin32\bin 

(3).解压缩gcc，替换GCCDIR路径 base.mk中 GCCDIR := c:/progra~1/GCC/arm-2015q1/bin

进入Customization_Kit_buildspec执行

make BBCHIP=MT6771会编译出MTK_AllnOne_DA.bin (DA_BR)

make BBCHIP=MT6771 DA_PL=yes 会编译出DA_PL

**2.签名DA**

Security2.1 DA_BR和DA_PL都需要使用python脚本进行sign

sign DA_PL: da_prvk.pem 要与preloader中的dakey.h中的key要配对 
Sign DA_BR: da_prvk.pem要与authifle中的DAA key要配对 由于dekay.h是根据root的publicｋkey转化的(可见dekay.h的生成)，所以获 取rootkey的private key来作为da的签名
