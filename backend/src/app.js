// backend/src/app.js

import express from "express";
import cors from "cors";

import schemeRoutes from "./routes/schemeRoutes.js";
import searchRoutes from "./routes/searchRoutes.js";
import chatRoutes from "./routes/chatRoutes.js";

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
app.use("/api/search", searchRoutes);
app.use("/api/chat", chatRoutes);

export default app;