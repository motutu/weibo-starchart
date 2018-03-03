#!/usr/bin/env node

const childProcess = require('child_process');
const fs = require('fs');
const path = require('path');
const process = require('process');

const fileUrl = require('file-url');
const mkdirp = require('mkdirp');
const puppeteer = require('puppeteer');

const date = process.argv[2];
let m = /^(\d{4})(\d{2})(\d{2})$/.exec(date);
if (!m) {
  console.log(`usage: ${process.argv[1]} YYYYMMDD`);
  process.exit(1);
}
const yyyy = m[1];
const mm = m[2];
const dd = m[3];
const htmlPath = path.resolve(__dirname, 'data', date, 'rendered.html');
if (!fs.existsSync(htmlPath)) {
  console.error(`${htmlPath} does not exist`);
  process.exit(1);
}
const shotsDir = path.resolve(__dirname, 'public', yyyy, mm, dd);
mkdirp.sync(shotsDir);

puppeteer.launch().then(async browser => {
  const page = await browser.newPage();
  await page.setViewport({
    width: 3840,
    height: 2160,
    deviceScaleFactor: 3
  });
  await page.goto(fileUrl(htmlPath));
  const tables = await page.$$('table[id]');
  for (let table of tables) {
    const idHandle = await table.getProperty('id');
    const id = await idHandle.jsonValue();
    await idHandle.dispose();
    await page.waitForSelector(`#${id}`, { visible: true });
    const shotPath = path.resolve(shotsDir, `${id}.png`);
    await table.screenshot({ path: shotPath });
    console.log(shotPath);
    try {
      childProcess.execFileSync('optipng', [shotPath]);
    } catch (err) {
      console.error(err.message);
    }
  }
  await browser.close();
});
