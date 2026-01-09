# Genie TTS Server

## 1. 项目简介

**Genie TTS** 是一款基于 **GPT-SoVITS** 架构的高性能语音合成（TTS）推理服务。

**核心优势：**

* **高性能推理：** 针对推理速度进行了深度优化。
* **低硬件门槛：** 无需昂贵的 GPU 显卡，在普通的 **CPU 服务器** 上即可流畅运行。
* **部署便捷：** 简单的 Python 环境配置即可启动服务。

**介绍视频：**

- [视频1](https://www.bilibili.com/video/BV1BHmzBtEjP)

---

## 2. 环境准备与安装

### 2.1 获取模型资源

首先，请前往 Gitee 仓库下载必要的模型文件和数据资源。

* **下载地址：** [https://ai.gitee.com/ppnt/Genie](https://ai.gitee.com/ppnt/Genie)
* **所需文件：** 请下载 `GenieData` 和 `CharacterModels` 两个文件夹。

### 2.2 安装依赖库

在您的 Python 环境中运行以下命令安装推理所需的依赖包：

```bash
pip install lameenc
pip install genie-tts

```

### 2.3 目录结构配置

将下载好的资源放置在 `genie_tts_server.py` 同级目录下。您的项目目录结构应如下所示：

```text
Project_Root/
├── genie_tts_server.py    # 启动脚本
├── GenieData/             # 下载的数据资源
└── CharacterModels/       # 下载的角色模型

```

---

## 3. 服务启动

确认文件放置正确后，使用以下命令启动推理服务：

```bash
python genie_tts_server.py

```

*默认服务端口通常为 `8000`（具体视脚本内部配置而定）。*

---

## 4. API 接口说明

服务启动后，您可以通过 HTTP POST 请求调用语音合成接口。

### 接口详情

* **URL:** `http://127.0.0.1:8000/tts`
* **Method:** `POST`
* **Content-Type:** `application/json`

### 请求参数 (JSON Body)

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `character_name` | String | 是 | 指定说话的角色名称 (需在 `CharacterModels` 中存在)，例如 `"feibi"`。 |
| `text` | String | 是 | 需要合成的文本内容。 |
| `split_sentence` | Boolean | 否 | 是否开启自动分句 (推荐 `true` 以获得更自然的停顿)。 |

### 调用示例 (cURL)

您可以直接复制以下命令在终端进行测试：

```bash
curl --location --request POST 'http://127.0.0.1:8000/tts' \
--header 'Content-Type: application/json' \
--data-raw '{
    "character_name": "feibi",
    "text": "天空为什么是蓝色的？这是一个困扰了人类很久的问题。当太阳光照射到地球大气层时，会发生一系列复杂的物理现象。我们看到的蓝天，实际上是阳光与大气中微小粒子相互作用的结果。让我们一起探索这个美丽现象背后的科学原理。",
    "split_sentence": true
}' --output output.mp3

```

> **注意：** 建议在 curl 命令末尾添加 `--output output.mp3`，以便直接将返回的二进制流保存为音频文件。

### 响应说明

* **成功响应：** 返回 **MP3 格式** 的音频二进制流。
* **播放方式：** 保存为 `.mp3` 文件后即可使用任意播放器播放。
