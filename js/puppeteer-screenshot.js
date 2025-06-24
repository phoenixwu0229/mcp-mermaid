#!/usr/bin/env node

/**
 * Puppeteer截图脚本
 * 用于将HTML文件转换为PNG图片
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function screenshot(htmlFile, outputFile, options = {}) {
    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--disable-extensions',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--force-color-profile=srgb',
            '--enable-font-antialiasing',
            '--font-render-hinting=slight',
            '--disable-font-subpixel-positioning=false'
        ]
    });

    try {
        const page = await browser.newPage();

        // 设置视口大小
        await page.setViewport({
            width: options.width || 1600,
            height: options.height || 1200,
            deviceScaleFactor: options.scale || 3
        });

        // 加载HTML文件
        const fileUrl = `file://${path.resolve(htmlFile)}`;
        console.log(`Loading: ${fileUrl}`);

        await page.goto(fileUrl, {
            waitUntil: ['networkidle0', 'domcontentloaded']
        });

        // 等待Mermaid渲染完成 - 使用新的检测机制
        let element;
        let boundingBox;

        try {
            // 首先等待.mermaid容器
            await page.waitForSelector('.mermaid', { timeout: 5000 });
            console.log('找到.mermaid容器');

            // 等待Mermaid.js加载完成
            await page.waitForFunction('typeof mermaid !== "undefined"', { timeout: 10000 });
            console.log('Mermaid.js加载完成');

            // 等待渲染完成标记
            await page.waitForFunction('window.mermaidReady === true', { timeout: 20000 });
            console.log('Mermaid渲染完成标记检测到');

            // 确保SVG元素存在
            await page.waitForSelector('.mermaid svg', { timeout: 5000 });
            console.log('找到SVG元素');

            // 额外等待确保渲染稳定
            await new Promise(resolve => setTimeout(resolve, 2000));

            element = await page.$('.mermaid svg');
            boundingBox = await element.boundingBox();

        } catch (error) {
            console.log('等待SVG失败，尝试等待其他元素...');

            // 添加调试信息 - 检查页面内容
            const mermaidContent = await page.$eval('.mermaid', el => el.innerHTML);
            console.log('Mermaid容器内容:', mermaidContent);

            const pageContent = await page.content();
            console.log('页面是否包含mermaid脚本:', pageContent.includes('mermaid'));

            // 检查是否有JavaScript错误
            const errors = await page.evaluate(() => {
                return window.errors || [];
            });
            console.log('JavaScript错误:', errors);

            // 如果SVG等待失败，尝试等待整个.mermaid容器
            try {
                await new Promise(resolve => setTimeout(resolve, 5000)); // 额外等待时间
                element = await page.$('.mermaid');
                boundingBox = await element.boundingBox();
                console.log('使用.mermaid容器作为截图区域');
            } catch (fallbackError) {
                throw new Error(`无法找到可截图的元素: ${error.message}`);
            }
        }

        if (!boundingBox) {
            throw new Error('无法获取SVG元素边界框');
        }

        // 截图（包含整个SVG元素）
        await page.screenshot({
            path: outputFile,
            type: 'png',
            clip: {
                x: Math.max(0, boundingBox.x - 20),
                y: Math.max(0, boundingBox.y - 20),
                width: boundingBox.width + 40,
                height: boundingBox.height + 40
            }
        });

        console.log(`Screenshot saved: ${outputFile}`);
        return true;

    } catch (error) {
        console.error('截图失败:', error.message);
        return false;
    } finally {
        await browser.close();
    }
}

// 解析命令行参数
function parseArgs() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('用法: node puppeteer-screenshot.js <html_file> <output_file> [options]');
        process.exit(1);
    }

    const htmlFile = args[0];
    const outputFile = args[1];
    const options = {};

    // 解析可选参数
    for (let i = 2; i < args.length; i += 2) {
        const key = args[i];
        const value = args[i + 1];

        switch (key) {
            case '--width':
                options.width = parseInt(value);
                break;
            case '--height':
                options.height = parseInt(value);
                break;
            case '--scale':
            case '--device-scale-factor':
                options.scale = parseFloat(value);
                break;
        }
    }

    return { htmlFile, outputFile, options };
}

// 主函数
async function main() {
    const { htmlFile, outputFile, options } = parseArgs();

    if (!fs.existsSync(htmlFile)) {
        console.error(`HTML文件不存在: ${htmlFile}`);
        process.exit(1);
    }

    const success = await screenshot(htmlFile, outputFile, options);
    process.exit(success ? 0 : 1);
}

if (require.main === module) {
    main().catch(error => {
        console.error('执行失败:', error);
        process.exit(1);
    });
}

module.exports = { screenshot }; 