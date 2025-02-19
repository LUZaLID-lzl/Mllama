### 客制化NVRAM步骤

##### 1.NVRAM数据结构定义

vendor/mediatek/proprietary/custom/HGZJ/cgen/cfgfileinc/CFG_HG_Custom_File.h

```c++
#ifndef _CFG_CUSTOM1_FILE_H
#define _CFG_CUSTOM1_FILE_H

typedef struct{
	unsigned int Array[512];
}File_Custom1_Struct;

#define CFG_FILE_CUSTOM1_REC_SIZE sizeof(File_Custom1_Struct)
#define CFG_FILE_CUSTOM1_REC_TOTAL 1

#endif
```



##### 2.初始化自定义NVRAM结构体的默认值

vendor/mediatek/proprietary/custom/HGZJ/cgen/cfgdefault/CFG_HG_Custom_Default.h

```c++
#ifndef _CFG_HG_CUSTOM_D_H
#define _CFG_HG_CUSTOM_D_H

File_HG_Custom_Struct stHGCustomDefault = {
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0
};

#endif
```



##### 3.在CUSTOM_CFG_FILE_LID中添加LID ID定义

vendor/mediatek/proprietary/custom/HGZJ/cgen/inc/Custom_NvRam_LID.h

```c
AP_CFG_CUSTOM_FILE_HG_CUSTOM_LID,
AP_CFG_CUSTOM_FILE_MAX_LID,
```

注意：枚举定义中的Lid顺序不能更改，而且新加的LID必须在AP_CFG_CUSTOM_FILE_MAX_LID之前



##### 4.给自定义的LID添加版本定义

vendor/mediatek/proprietary/custom/HGZJ/cgen/inc/Custom_NvRam_LID.h

```c
/* custom2 file version */
#define AP_CFG_CUSTOM_FILE_CUSTOM2_LID_VERNO "000"

#define AP_CFG_CUSTOM_FILE_HG_CUSTOM_LID_VERNO "000"
```



##### **5.将自己新增CFG_HG_Custom_File.h和CFG_HG_Custom_Default.h分别include到对应的文件目录中**

vendor/mediatek/proprietary/custom/HGZJ/cgen/inc/custom_cfg_module_default.h

```c
#include "../cfgdefault/CFG_HG_Custom_Default.h"
```

vendor/mediatek/proprietary/custom/HGZJ/cgen/inc/custom_cfg_module_file.h

```c
#include "../cfgfileinc/CFG_HG_Custom_File.h"
```



##### 6.将新增的NVRAM相关的信息添加到NVRAM数组中去

vendor/mediatek/proprietary/custom/HGZJ/cgen/inc/CFG_file_info_custom.h

```c
{ "/mnt/vendor/nvdata/APCFG/APRDCL/hg_custom", VER(AP_CFG_CUSTOM_FILE_HG_CUSTOM_LID),
CFG_FILE_HG_CUSTOM_REC_SIZE,
CFG_FILE_HG_CUSTOM_REC_TOTAL, SIGNLE_DEFUALT_REC, (char *)&stHGCustomDefault,
DataReset, NULL
},
```



##### 7.将新增的NVRAM相关的信息添加到inc/Custom_NvRam_data_item.h中

//Meta tool需要读取的信息

vendor/mediatek/proprietary/custom/HGZJ/cgen/inc/Custom_NvRam_data_item.h

```c
LID_BIT VER_LID(AP_CFG_CUSTOM_FILE_HG_CUSTOM_LID)
File_HG_Custom_Struct *CFG_FILE_HG_CUSTOM_REC_TOTAL{

};
```



##### 8.将NVRAM file添加到备份列表中

vendor/mediatek/proprietary/external/nvram/libcustom_nvram/CFG_file_info.c

```c
#ifdef MTK_SCP_SMARTPA_SUPPORT
{"smartpa_calib", AP_CFG_CUSTOM_FILE_SMARTPA_CALIB_LID},
#endif
{"hg_custom", AP_CFG_CUSTOM_FILE_HG_CUSTOM_LID} //gaowei
```



##### 9.结果验证

```log
04-07 07:26:54.735 2837 2837 D NVRAM : Please make sure size for special lid in new nvram
partition should alignment 512
04-07 07:26:54.735 2837 2837 E /vendor/bin/hw/vendor.mediatek.hardware.nvram@1.1-service: open file
Error!
```

注意事项：

如平台使用的是【eMMC】，新LID对应struct的size必须是512 byte的倍数；

如平台使用的是【NAND】，新LID对应struct的size必须是page size对齐（即4K或2K）