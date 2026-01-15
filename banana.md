# 图片编辑（Nano-banana 支持比例）

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /v1beta/models/{model}:generateContent:
    post:
      summary: 图片编辑（Nano-banana 支持比例）
      deprecated: false
      description: >-
        官方文档：https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn#optional_configurations
      tags:
        - 模型接口/Google/Google Gemini接口
      parameters:
        - name: model
          in: path
          description: ''
          required: true
          example: gemini-2.5-flash-image-preview
          schema:
            type: string
        - name: Authorization
          in: header
          description: ''
          required: true
          example: sk-
          schema:
            type: string
        - name: Content-Type
          in: header
          description: ''
          required: false
          example: application/json
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                contents:
                  type: array
                  items:
                    type: object
                    properties:
                      parts:
                        type: array
                        items:
                          type: object
                          properties:
                            text:
                              type: string
                          x-apifox-orders:
                            - text
                    x-apifox-orders:
                      - parts
                    required:
                      - parts
                generationConfig:
                  type: object
                  properties:
                    responseModalities:
                      type: array
                      items:
                        type: string
                    imageConfig:
                      type: object
                      properties:
                        aspectRatio:
                          type: string
                          description: //枚举1:1、9:16、16:9、3:4、4:3、3:2、2:3、5:4、4:5、21:9
                        imageSize:
                          type: string
                          description: // gemini-3-pro-image-preview使用，清晰度可选：2K、4K
                      x-apifox-orders:
                        - aspectRatio
                        - imageSize
                      required:
                        - aspectRatio
                        - imageSize
                  x-apifox-orders:
                    - responseModalities
                    - imageConfig
                  required:
                    - responseModalities
              required:
                - contents
                - generationConfig
              x-apifox-orders:
                - contents
                - generationConfig
            example:
              contents:
                - role: user
                  parts:
                    - inlineData:
                        mimeType: image/png
                        data: 图片的base64数据，目前只支持base64
                    - text: 将车的颜色变为黑色，天空的颜色变为白色
              generationConfig:
                responseModalities:
                  - IMAGE
                imageConfig:
                  aspectRatio: '16:9'
                  imageSize: 2K
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties: {}
                x-apifox-orders: []
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 模型接口/Google/Google Gemini接口
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/6819841/apis/api-359803228-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```