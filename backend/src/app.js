// backend/src/app.js

import express from "express";
import cors from "cors";
import schemeRoutes from "./routes/schemeRoutes.js";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    service: "Yojana Mitra API"
  });
});

app.use("/api/schemes", schemeRoutes);

export default app;