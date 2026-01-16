export function buildMultiviewPrompt(productName: string): string {
  const name = productName?.trim() || "商品";
  return `${name}，生成单张2x2四宫格白底商品图，四个角度：正面、45度侧面、背面、俯视。纯白背景，柔和棚拍光，产品居中，无道具无文字无水印，边距一致。`;
}
