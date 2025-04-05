import express from 'express';
const router = express.Router();
import { upworkScraperController } from './upWorkController.js';

router.get('/jobs', async (req, res) => {
    try {
        const { q: keywords, page } = req.query;

        const allJobs = await upworkScraperController(keywords, page);
        res.status(200).json(allJobs);
    } catch (err) {
        console.log('Error getting jobs:', err);
        res.status(500).json({ msg: 'Error getting jobs' });
    }
});

export default router;
