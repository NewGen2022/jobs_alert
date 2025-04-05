import { main } from '../jobsScraper/upworkScraper.js';

const upworkScraperController = (keywords, page) => {
    // RUN UPWORK SCRAPER
    return main(keywords, page);
};

export { upworkScraperController };
