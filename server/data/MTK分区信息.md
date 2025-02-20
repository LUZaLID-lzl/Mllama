1. preloader
    
2. - Store the first-stage bootloader.
        
3. DSP_BL
    
4. - DSP Boot Loader.
        
5. MBR、EBR1、EBR2
    
6. - Ext4 file system partition index table.
        
7. PMT
    
8. - Partition management table.
        
9. pgpt
    
10. - Store the Primary Guid Partition Table.
        
11. boot_para
    
12. - MTK in house parameter for boot up sequence.
        
13. recovery
    
14. - Store the kernel and ramdisk for recovery boot.
        
15. recovery_ramdisk
    
16. - Store recovery_ramdisk image.
        
17. recovery_vendor
    
18. - Store recovery_vendor image.
        
19. para
    
20. - Store Google recovery data, system env and other misc info, which is used in lk and kernel.
        
21. custom
    
22. - Store custom image data.
        
23. expdb
    
24. - Store Exception data.
        
25. frp
    
26. - Store google factory reset protection info.
        
27. nvcfg
    
28. - nvram config which will not be wiped when OTA update or factory reset.
        
29. nvdata
    
30. - Store nvram data.
        
31. metadata
    
32. - Store the master key for encryption.
        
33. oemkeystore
    
34. - Container to store public key for verified boot.
        
35. keystore
    
36. - Container to store public key for verified boot.
        
37. protect1 or protect_f
    
38. - Store SIM_ME lock data.
        
39. protect2 or protect_s
    
40. - Store backup copy of SIM_ME lock data.
        
41. SEC_RO or SECRO
    
42. - Reserved for the security platform used.
        
43. Misc
    
44. - Used for the recovery procedure (power loss).
        
45. seccfg
    
46. - Store security partition configure information.
        
47. persist
    
48. - Store DRM/KeyInstall security data.
        
49. sec1
    
50. - Container to store public key for verified boot.
        
51. proinfo
    
52. - Store Product Info of Mobile Phone or vendor.
        
53. efuse
    
54. - Store customer effuse bits(mainly security keys) .
        
55. md1img
    
56. - Store modem image.
        
57. md1dsp
    
58. - Store modem image.
        
59. md1arm7
    
60. - Store modem image.
        
61. md3img
    
62. - Store modem image.
        
63. mcupmfw
    
64. - MediaTek in-house ASIC for cpu power management.
        
65. spmfw
    
66. - MediaTek in-house ASIC for power management.
        
67. scp1
    
68. - Store Tinysis SCP image.
        
69. scp2
    
70. - Backup for scp1.
        
71. sspm_1
    
72. - MediaTek in-house ASIC for power management under secure world.
        
73. sspm_2
    
74. - Backup for sspm_1.
        
75. cam_vpu1
    
76. - store camera vpu binary for in-house alg.
        
77. cam_vpu2
    
78. - store camera vpu binary for in-house alg.
        
79. cam_vpu3
    
80. - store camera vpu binary for in-house alg.
        
81. gz1
    
82. - Firmware partition for memory management function.
        
83. gz2
    
84. - Backup for gz1.
        
85. nvram
    
86. - Store Calibration data of IMEI/BT/Wifi.
        
87. lk
    
88. - Store Uboot/LK image.
        
89. lk2
    
90. - backup for lk.
        
91. boot
    
92. - Store the kernel and ramdisk for normal boot.
        
93. logo
    
94. - Store logo data showing during charging.
        
95. odmdtbo or dtbo
    
96. - For device tree overlay.
        
97. tee1
    
98. - Store ARM trusted firmware and TEE binary.
        
    - Trusted Excution Environment: [https://www.trustonic.com/technology/trustzone-and-tee](https://www.trustonic.com/technology/trustzone-and-tee)
        
99. tee2
    
100. - Backup of tee1.
        
101. odm
    
102. - Store odm image.
        
103. vendor
    
104. - Store vendor image.
        
105. system
    
106. - Store system image.
        
107. vbmeta
    
108. - Store vbmeta image used for AVB2.0 .
        
109. cache
    
110. - Store Android internal cache data or web cache data.
        
111. eng_system
    
112. - MTK Internal Only.
        
113. eng_vendor
    
114. - MTK Internal Only.
        
115. userdata
    
116. - User Storage Area.
        
117. intsd
    
118. - Internal sdcard on emmc.
        
119. otp
    
120. - Otp(one time program) area on emmc.
        
121. flashinfo
    
122. - Flash tool download information.
        
123. BMTPOOL
    
124. - Handles Bad Block Management（nandflash used and reserved on emmc）.
        
125. ppl
    
126. - Privacy protection lock，used for mobile phone antitheft.
        
127. loader_ext1
    
128. - Store preloader extension image.
        
129. loader_ext2
    
130. - Backup for loader_ext2.
        
131. sgpt
    
132. - Backup of pgpt.