function textToImage(text, options = {}) {
    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")

    const baseWidth = options.width || 800
    const padding = options.padding || 10
    const lineHeight = options.lineHeight || 24
    const font = options.font || "16px Arial"
    const scale = options.scale || 3  // 放大两倍像素

    ctx.font = font

    function wrapText(text, maxWidth) {
        const words = text.split(" ")
        const lines = []
        let line = ""
        for (let n = 0; n < words.length; n++) {
            const testLine = line + (line ? " " : "") + words[n]
            const metrics = ctx.measureText(testLine)
            if (metrics.width > maxWidth && line) {
                lines.push(line)
                line = words[n]
            } else {
                line = testLine
            }
        }
        if (line) lines.push(line)
        return lines
    }

    const lines = wrapText(text, baseWidth - padding * 2)
    const height = lines.length * lineHeight + padding * 2

    canvas.width = baseWidth * scale
    canvas.height = height * scale
    ctx.scale(scale, scale)  // 按比例缩放绘制

    ctx.fillStyle = options.background || "#fff"
    ctx.fillRect(0, 0, baseWidth, height)

    ctx.fillStyle = options.color || "#333"
    ctx.textBaseline = "top"
    ctx.font = font

    lines.forEach((line, index) => {
        ctx.fillText(line, padding, padding + index * lineHeight)
    })

    return canvas.toDataURL("image/png")
}


export {textToImage};