# 全能视频S-官方-图生视频-支持真人

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /openapi/v2/rhart-video-s-official/image-to-video-realistic:
    post:
      summary: 全能视频S-官方-图生视频-支持真人
      deprecated: false
      description: ''
      tags:
        - 视频生成（新）/全能视频 S
      parameters:
        - name: Content-Type
          in: header
          description: ''
          required: false
          example: application/json
          schema:
            type: string
        - name: Authorization
          in: header
          description: ''
          example: Bearer 834a792dc64d419f85592f1e57145745
          schema:
            type: string
            default: Bearer 834a792dc64d419f85592f1e57145745
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                prompt:
                  type: string
                  title: 提示词
                resolution:
                  type: string
                  title: 分辨率
                  enum:
                    - 720p
                    - 1080p
                  x-apifox-enum:
                    - value: 720p
                      name: ''
                      description: ''
                    - value: 1080p
                      name: ''
                      description: ''
                aspectRatio:
                  type: string
                  title: 比例
                  enum:
                    - '16:9'
                    - '9:16'
                  x-apifox-enum:
                    - value: '16:9'
                      name: ''
                      description: ''
                    - value: '9:16'
                      name: ''
                      description: ''
                  default: '16:9'
                imageUrl:
                  type: string
                  title: 图片地址
                duration:
                  type: string
                  title: 视频时长
                  enum:
                    - '4'
                    - '8'
                    - '12'
                  x-apifox-enum:
                    - value: '4'
                      name: ''
                      description: ''
                    - value: '8'
                      name: ''
                      description: ''
                    - value: '12'
                      name: ''
                      description: ''
              x-apifox-orders:
                - prompt
                - resolution
                - aspectRatio
                - imageUrl
                - duration
              required:
                - prompt
                - resolution
                - aspectRatio
                - imageUrl
                - duration
              x-apifox-ignore-properties: []
            examples: {}
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/%E7%94%9F%E6%88%90%E4%BB%BB%E5%8A%A1%E6%8F%90%E4%BA%A4%E7%BB%93%E6%9E%9C
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 视频生成（新）/全能视频 S
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/6103976/apis/api-402608271-run
components:
  schemas:
    生成任务提交结果:
      type: object
      properties:
        taskId:
          type: string
          title: 任务ID
        status:
          type: string
          title: 状态
          enum:
            - QUEUED
            - RUNNING
            - FAILED
            - SUCCESS
          x-apifox-enum:
            - value: QUEUED
              name: 进入执行队列
              description: ''
            - value: RUNNING
              name: 运行中
              description: ''
            - value: FAILED
              name: 失败
              description: ''
            - value: SUCCESS
              name: 成功
              description: ''
        errorCode:
          type: string
          title: 错误码
          nullable: true
        errorMessage:
          type: string
          title: 错误信息
          nullable: true
        results:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                title: 结果链接
              outputType:
                type: string
                title: 输出类型
            x-apifox-orders:
              - url
              - outputType
            required:
              - url
              - outputType
            x-apifox-ignore-properties: []
          title: 结果
        clientId:
          type: string
          nullable: true
        promptTips:
          type: string
          nullable: true
      required:
        - taskId
        - status
        - errorCode
        - errorMessage
        - results
        - clientId
        - promptTips
      x-apifox-orders:
        - taskId
        - status
        - errorCode
        - errorMessage
        - results
        - clientId
        - promptTips
      x-apifox-ignore-properties: []
      x-apifox-folder: ''
  securitySchemes: {}
servers:
  - url: https://www.runninghub.cn
    description: runninghub.cn
security: []

```