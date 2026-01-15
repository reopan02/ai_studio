# 视频状态

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /v1/videos/{video_id}:
    get:
      summary: 视频状态
      deprecated: false
      description: 查询创建视频的状态
      tags:
        - 模型接口/sora2/官方格式
      parameters:
        - name: video_id
          in: path
          description: ''
          required: true
          example: video_123
          schema:
            type: string
        - name: Authorization
          in: header
          description: ''
          required: false
          example: Bearer sk-
          schema:
            type: string
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
                model: sora2_video_generation
                status: completed
                progress: 100
                created_at: 1760286060
                completed_at: 1760286194
                seconds: '4'
                size: 720x1280
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 模型接口/sora2/官方格式
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/6819841/apis/api-359887121-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```