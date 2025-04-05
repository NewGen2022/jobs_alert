import express from 'express';
import upworkJobsRouter from './upWorkRoutes.js';

const server = express();

server.use(express.json());

const PORT = process.env.PORT || 3003;

server.use('/api/upwork', upworkJobsRouter);

server.listen(PORT, () => {
    console.log('Server is running on port:', PORT);
});
