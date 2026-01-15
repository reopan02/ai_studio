# 获取视频

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /v1/videos/{video_id}/content:
    get:
      summary: 获取视频
      deprecated: false
      description: 获取视频
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
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 模型接口/sora2/官方格式
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/6819841/apis/api-359887147-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```