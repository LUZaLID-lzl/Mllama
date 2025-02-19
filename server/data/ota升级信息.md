ErrorCode::kSuccess (0) 升级成功

ErrorCode::kSuccess (1) 升级失败

ErrorCode::kFilesystemCopierError (4) 未知，暂时未使用的错误码

ErrorCode::kPostinstallRunnerError (5) 升级安装结束，设置启动分区失败

ErrorCode::kPayloadMismatchedType (6) 升级包的升级类型不匹配或升级包minor version不兼容

ErrorCode::kInstallDeviceOpenError (7) 无法启动升级。可能是原因：分区错误，设备支持升级的分区和升级包内的不匹配；设备处于disable-verity状态；

ErrorCode::kKernelDeviceOpenError (8) 未知，暂时未使用的错误码

ErrorCode::kDownloadTransferError (9) w，找不到升级包

ErrorCode::kPayloadHashMismatchError (10) FILE_HASH值不匹配

ErrorCode::kPayloadSizeMismatchError (11) 数据size不匹配

ErrorCode::kDownloadPayloadVerificationError (12) 签名验证失败

ErrorCode::kDownloadStateInitializationError (20) 升级包写入时失败 一般都是发生在差分包升级时，检测boot、system、vendor的hash值不匹配。

ErrorCode::kDownloadInvalidMetadataMagicString (21) 未找到正确bin文件，一般是offset不对导致

ErrorCode::kDownloadInvalidMetadataSize (32) METADATA_SIZE值不匹配

ErrorCode::kPayloadTimestampError (51) 升级包的date比机器当前版本早

