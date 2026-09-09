# GVHMR 视频推理

本目录来自 humanoid-lab 的 GVHMR 快照，服务于 Tracking_single 的视频输入阶段。

- [安装、CUDA 和模型目录](../../docs/01_install.md)
- [完整视频运行步骤与排错](../../docs/02_video.md)
- [逐文件 API 与教程索引](../../docs/code_reference.md)
- [原始许可](LICENSE)

主要入口是 `tools/demo/demo.py` 和 `tools/demo/demo_folder.py`。输入先重采样到 30 fps，输出 `hmr4d_results.pt` 交给 GMR。推理支持固定相机或 SimpleVO；本版不包含 GVHMR 重训练数据集和 DPVO。

[上游原始 README](README.upstream.md) 完整保留论文引用、作者和致谢，其中完整项目的其他命令不属于本提取版；当前操作以本页链接的教程为准。缺失的 ViTPose builder 从官方固定提交补回，来源记录在 `../../docs/upstream_recovery.json`。
