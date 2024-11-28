# mai-gen-videob50

自动从流媒体上搜索并构建你的舞萌DX B50视频
Auto search and generate your best 50 videoes of MaimaiDX

## 快速开始

想要一键（几乎）自动地生成你的B50视频？参考你是否符合以下条件：

- 你拥有一个[水鱼查分器](https://www.diving-fish.com/maimaidx/prober/)账号，并允许公开获取你的B50数据

- 你的网络环境可以正常访问[Youtube](https://www.youtube.com/)

> 由于目前的谱面确认视频获取方法为从Youtube上抓取，你可能需要开启网络代理🪜才可以正常使用，非常抱歉！（请放心生成器只抓取360p的预览视频，因此对网络速度和流量的要求很低）

> 我们正在考虑后续开发抓取B站的可选项，敬请期待。

- 你具有基本的计算机知识，可以按照说明（或GPT辅助）完成python脚本操作

如果一切OK，请参考[使用说明](#使用说明)开始生成你的B50视频!

我正在制作一个教程视频，稍后会贴在这里


## 当前生成效果预览

![alt text](md_res/image.png)

## 使用说明

### 环境安装和准备工作

1. 推荐使用 `conda` 安装python环境和依赖

    ```bash
    conda create -n mai-gen-videob50 python=3.10
    conda activate mai-gen-videob50
    ```

2. 从 requirements.txt 安装依赖

    ```bash
    pip install -r requirements.txt
    ```

3. 安装必要的工具软件：

    请确保`ffmpeg`（用于视频的编码和解码）可以在你的系统命令行或终端中正常使用：

    - Windows:

        从 [CODEX FFMPEG](https://www.gyan.dev/ffmpeg/builds/) 下载 `ffmpeg-release-essentials.zip` 文件，解压文件到你的电脑上的任意目录后，将 `bin` 目录所在路径添加到系统环境变量中。

        > 如果你不了解如何配置系统环境变量，请自行搜索相关教程。配置完环境变量后需要重启终端方可生效
    
    - Linux:

        使用以下命令安装ffmpeg：

        ```bash
        sudo apt-get install -y ffmpeg
        ```

### 测试系统的功能是否正常

运行 `test.py` ：

```bash
python test.py
```

如果程序输出以下内容，并可以在`./videos/test`文件夹下获得一个`test_video.mp4`的17秒钟视频文件，则说明系统功能正常。

```
##### 开始系统功能测试...

## [1/3]测试网络代理配置...
当前代理设置:
127.0.0.1:7890
## [1/3]网络测试成功

## [2/3]测试图片生成功能...
未找到乐曲11663的难度4的max dx score信息。
## [2/3]图片生成测试成功

## [3/3]测试视频生成功能...
正在合成视频片段: intro_1
正在合成视频片段: NewBest_1
正在合成视频片段: ending_1
MoviePy - Building video videos/test/test_video.mp4.
MoviePy - Writing audio in test_videoTEMP_MPY_wvf_snd.mp3
MoviePy - Done.
MoviePy - Writing video videos/test/test_video.mp4
...
MoviePy - video ready videos/test/test_video.mp4
## [3/3]视频生成测试成功
#####全部系统功能测试完成！
```

如果未能正常执行测试，请检查你的python环境和`ffmpeg`是否安装正确，确保其路径已添加到系统环境变量中。

如无法自行确认问题，可将错误输出粘贴到issue中（在发issue前请先搜索是否已有相同问题）。

### 相关参数配置

在 `global_congfig.yaml` 文件中，配置以下信息：

- `HTTP_PROXY` ：本项目当前从youtube上搜索和下载谱面确认视频，可能需要开启网络代理才可以正常访问，将其设置为你的代理地址（如果你使用clash等代理工具，请设置为`"127.0.0.1:7890"`）。

- `USER_ID` ：设置为你的水鱼用户ID。

    > 为了能抓取到精确的成绩信息，请在[舞萌 DX | 中二节奏查分器](https://www.diving-fish.com/maimaidx/prober/)中点击“编辑个人资料”，并取消勾选“对非网页查询的成绩使用掩码”。

- `SEARCH_MAX_RESULTS` ：设置为从youtube上搜索视频时，最多搜索到的视频数量。

- `VIDEO_RES` ：设置输出视频的分辨率，格式为`(width, height)`。

- `VIDEO_TRANS_ENABLE` ：设置生成完整视频时，是否启用视频片段之间的过渡效果，默认为`true`，会在每个视频片段之间添加过渡效果。

- `VIDEO_TRANS_TIME` ：设置生成完整视频时，两个视频片段之间的过渡时间，单位为秒。

- `USE_ALL_CACHE` ：生成图片和视频需要一定时间。如果设置为`true`，则使用本地已经生成的缓存，从而跳过重新生成的步骤，推荐在已经获取过数据但是合成视频失败或中断后使用。如果你需要从水鱼更新新的b50数据，请设置为`false`。

- `ONLY_GENERATE_CLIPS` ：设置为是否只生成视频片段，如果设置为`true`，则只会在`./videos/{USER_ID}`文件夹下生成每个b的视频片段，而不会生成完整的视频。


### 完整B50视频生成操作流程

0、配置好`global_congfig.yaml`文件，主要是配置代理以及填写`USER_ID`为你的水鱼用户名。

按照下面的步骤开始生成你的b50视频：

1. 运行`pre_gen.py`文件，程序将会自动查询您的最新b50数据，并抓取相关谱面确认视频。

    ```bash
    python pre_gen.py
    ```

    > 如果网络连接异常，请检查`global_congfig.yaml`文件中`HTTP_PROXY`是否配置正确。

    > 视网络情况，通常抓取完整的一份b50视频素材需要30-60分钟。如果在这一步骤期间遇到网络异常等问题导致程序中断，可以重新运行`pre_gen.py`文件，程序将会从上一次中断处继续执行。

2. 执行完毕后，请检查如下文件是否生成：

    在`./b50_datas`文件夹下可以找到一个`video_config_{USER_ID}.json`文件

    在`./b50_images/{USER_ID}`文件夹下可以找到所有生成的成绩图片，以`{PastBest/NewBest}_{id}.png`的格式命名。

    在`./videos/downloads`文件夹下可以找到所有已下载的谱面确认视频，命名格式为`{song_id}-{level_index}-{type}.mp4`。其中，`song_id`为曲目的ID，`level_index`为难度，`type`为谱面类型，例如`834-4-SD.mp4`。

    下面你需要手动进行如下操作（**我们正在考虑设计前端页面以优化这部分流程**）：

    - 打开`video_config_{USER_ID}.json`文件，在每条数据的`text`字段中填写你要展示的评论。

        - 其中，"intro"和"ending"部分你填写的text会作为开头和结尾的文字展示。"main"部分填写的text为每条b50下的文字展示。

        - 你输入的文字会根据模板长度自动换行，如果想要手动换行换行请使用`\n`，例如`aaa\nbbb`。请注意评论的长度，过长可能导致超出屏幕

        - 如果在一页的"intro"和"ending"部分想要展示的文字太多写不下，可以复制配置文件内容，修改为不同的id，以生成多页的intro和ending，例如：

        ```json
        "intro": [
            {
                "id": "intro_1",
                "duration": 10,
                "text": "【前言部分第一页】"
            },
            {
                "id": "intro_2",
                "duration": 10,
                "text": "【前言部分第二页】"
            }
        ],
        "ending": [
            {
                "id": "ending_1",
                "duration": 10,
                "text": "【后记部分第一页】"
            },
            {
                "id": "ending_2",
                "duration": 10,
                "text": "【后记部分第二页】"
            }
        ],
        ```
        - "main"的部分暂不支持多页文字。"main"部分的填写示例如下：

        ```json
        "main": [
            {
                "id": "NewBest_1",
                "achievement_title": "系ぎて-re:Master-DX",
                "song_id": 11663,
                "level_index": 4,
                "type": "DX",
                "main_image": "b50_images\\test\\PastBest_1.png",
                "video": "videos\\test\\11663-4-DX.mp4",
                "duration": 9,
                "start": 49,
                "end": 58,
                "text": "【请填写b50评价】\n【你只需要填写这条字符串】"
            },
        ]
        ```

        - 修改`start`/`end`的值可以调整每页的视频起止时间，如要修改，请同时修改对应的`duration`展示时长(单位为秒，"intro"和"ending"部分只需要配置`duration`即可)。

    - 在`./videos/downloads/{USER_ID}`文件夹下，检查抓取视频的正确性，每个视频会按照`曲目id-难度阶级-类型（SD或DX）.mp4`的格式命名，请对照`video_config_{USER_ID}.json`文件确认与b50无误。如果视频出现以下问题，请考虑手动修改或替换视频：

        - 视频对应的谱面确认和实际不符

        - 视频中谱面确认的画面没有位于视频的正中央（部分早期谱面可能出现此问题，因为往往只能抓取到到带有手元的视频），请考虑手动编辑视频将外录的谱面确认部分移动至视频中央，并**保持视频的分辨率和比例均不变**（可以两边用黑色填充）。

        - 替换视频时，请保证视频的文件名不变。

3. 检查完毕无误后，请运行`main_gen.py`文件，程序将会生成完整的视频（或每组视频片段）。

    ```bash
    python main_gen.py
    ```

    > 合并完整视频的时间取决于你设置的预览时长和设备的性能，在每个片段15s的情况下，生成完整视频大概需要30-40分钟。

## 鸣谢

- [舞萌 DX 查分器](https://github.com/Diving-Fish/maimaidx-prober) 提供数据库及查询接口

- [Tomsens Nanser](https://space.bilibili.com/255845314) 提供图片生成素材模板以及代码实现
