/**
 * DISCLAIMER:
 * This code is provided for educational and learning purposes only.
 * It is not intended for production use, nor is it intended to encourage or facilitate
 * unauthorized scraping of any website, including Upwork. Users are responsible for
 * ensuring that their use of this code complies with all applicable laws and the terms
 * of service of any target website. The author assumes no liability for any misuse
 * or consequences arising from the use of this code.
 */

import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
// import { rl, askQuestion } from './inputHelper.js';

puppeteer.use(StealthPlugin());

const browser = await puppeteer.launch(); // { headless: false }
const page = await browser.newPage();

// Set a custom user agent so the site loads full content.
await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
        'AppleWebKit/537.36 (KHTML, like Gecko) ' +
        'Chrome/91.0.4472.124 Safari/537.36'
);

const baseUrl = 'https://www.upwork.com';

const scrapeJobsPerPage = async (keywords, page, currentPage) => {
    console.log(
        `Starting scraper with keywords "${keywords}" for page ${currentPage}`
    );

    let url = `${baseUrl}/nx/search/jobs/?nbs=1&proposals=0-4,5-9,10-14,15-19&q=${keywords}&page=${currentPage}`;
    console.log(url);
    await page.goto(url);

    const jobsPerPage = await page.evaluate((baseUrl) => {
        // Inline helper to convert relative time to Unix timestamp (milliseconds)
        function parseRelativeTime(relativeStr) {
            const now = new Date().getTime();
            const lowerStr = relativeStr.toLowerCase();
            let diff = 0;
            if (lowerStr.includes('minute')) {
                const match = lowerStr.match(/(\d+)\s*minute/);
                if (match) {
                    diff = parseInt(match[1]) * 60 * 1000;
                }
            } else if (lowerStr.includes('hour')) {
                const match = lowerStr.match(/(\d+)\s*hour/);
                if (match) {
                    diff = parseInt(match[1]) * 60 * 60 * 1000;
                }
            } else if (lowerStr.includes('day')) {
                const match = lowerStr.match(/(\d+)\s*day/);
                if (match) {
                    diff = parseInt(match[1]) * 24 * 60 * 60 * 1000;
                } else if (lowerStr.includes('yesterday')) {
                    diff = 24 * 60 * 60 * 1000;
                }
            } else if (lowerStr.includes('week')) {
                const match = lowerStr.match(/(\d+)\s*week/);
                if (match) {
                    diff = parseInt(match[1]) * 7 * 24 * 60 * 60 * 1000;
                }
            } else if (lowerStr.includes('month')) {
                const match = lowerStr.match(/(\d+)\s*month/);
                if (match) {
                    diff = parseInt(match[1]) * 30 * 24 * 60 * 60 * 1000;
                }
            }
            return now - diff;
        }

        const jobElements = document.querySelectorAll(
            'article[data-test="JobTile"]'
        );
        return Array.from(jobElements).map((job) => {
            // JOB HEADER
            const jobHeader = job.querySelector('div.job-tile-header');
            const postingSpans = jobHeader.querySelectorAll(
                'small[data-test="job-pubilshed-date"] span'
            );
            const postingTime =
                postingSpans.length >= 2
                    ? postingSpans[1].textContent.trim()
                    : 'N/A';
            const postingTimestamp =
                postingTime !== 'N/A' ? parseRelativeTime(postingTime) : 'N/A';

            const titleLinkElement = jobHeader.querySelector(
                'h2.job-tile-title a'
            );
            const jobTitle = titleLinkElement
                ? titleLinkElement.textContent.trim()
                : 'No job title';
            const jobHrefRelative = titleLinkElement
                ? titleLinkElement.getAttribute('href')
                : 'No relative link';

            // JOB DETAILS
            const jobDetails = job.querySelector(
                'div[data-test="JobTileDetails"]'
            );
            const descriptionElement = jobDetails.querySelector(
                'div.air3-line-clamp p'
            );
            const description = descriptionElement
                ? descriptionElement.textContent.trim()
                : 'No description';

            const skillElements = jobDetails.querySelectorAll(
                'div[data-test="TokenClamp JobAttrs"] button[data-test="token"] span'
            );
            const skills = Array.from(skillElements).map((el) =>
                el.textContent.trim()
            );

            return {
                postingTimestamp,
                jobTitle,
                jobHref:
                    jobHrefRelative !== 'No relative link'
                        ? baseUrl + jobHrefRelative
                        : jobHrefRelative,
                description,
                skills,
            };
        });
    }, baseUrl);

    return jobsPerPage;
};

const main = async (keywords, currentPage) => {
    // const keywords = await askQuestion('Enter job keyword to search for: ');

    // commented when implemented API
    // rl.close();

    const allJobs = [];
    // let currentPage = 1;
    let jobsOnPage = [];
    // do {
    jobsOnPage = await scrapeJobsPerPage(keywords, page, currentPage);
    // console.log(`Jobs on page ${currentPage}:`, jobsOnPage);
    // if (jobsOnPage.length === 0)
    // break;
    allJobs.push(...jobsOnPage);
    currentPage++;
    // } while (jobsOnPage.length > 0);

    console.log('Total jobs found:', allJobs.length);

    // commented when implemented API
    // await browser.close();

    return allJobs;
};

export { main };
