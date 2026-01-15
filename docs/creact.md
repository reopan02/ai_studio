# 创建视频

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /v1/videos:
    post:
      summary: 创建视频
      deprecated: false
      description: "官方格式，异步任务。\n官方文档：https://platform.openai.com/docs/api-reference/videos/create\n此种格式需纯官转渠道才可调用，价格根据视频长度以及视频质量计算。\nsize：字符串格式\_{width}x{height}。可用分辨率依赖于模型选择：\n  sora-2：       1280x720, 720x1280   （官价1秒0.1刀）\n  sora-2-pro：1280x720, 720x1280,   （官价1秒0.3刀）\n                       1024x1792, 1792x1024（官价1秒0.5刀）\nseconds：视频长度，可选值为 “4”，“8”，“12”，默认是 “4”。\n例子：sora2分组倍率为5，视频4秒，分辨率1280x720，费用为0.1x4x5=2元；\n           sora2分组倍率为5，视频12秒，分辨率1024x1792，费用为0.5x12x5=30元"
      tags:
        - 模型接口/sora2/官方格式
      parameters:
        - name: Authorization
          in: header
          description: ''
          required: false
          example: Bearer sk-
          schema:
            type: string
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                prompt:
                  description: |
                    提示词
                  example: ''
                  type: string
                input_reference:
                  format: binary
                  type: string
                  description: 图像参考，支持 jpeg/png/webp，需匹配视频分辨率
                  example: ''
                model:
                  description: 模型名称，可选值为 “sora-2”，“sora-2-pro”
                  example: sora-2
                  type: string
                seconds:
                  description: 视频长度，默认4秒，可选值为 “4”，“8”，“12“
                  example: ''
                  type: string
                size:
                  description: |-
                    视频分辨率，默认720x1280，可选值为：
                    sora-2：1280x720, 720x1280
                    sora-2-pro：1280x720, 720x1280, 1024x1792, 1792x1024
                  example: ''
                  type: string
              required:
                - prompt
                - model
            examples: {}
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties: {}
              example:
                id: video_123
                object: video
                model: sora-2
                status: queued
                progress: 0
                created_at: 1712697600
                size: 1024x1808
                seconds: '8'
                quality: standard
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 模型接口/sora2/官方格式
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/6819841/apis/api-359887002-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```