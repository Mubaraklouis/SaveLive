require("dotenv").config();
const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { pool, connectDB } = require("./config/db");
const healthRoutes = require("./routes/health");
const usersRoutes = require("./routes/users");
const eventsRoutes = require("./routes/events");
const seedRoutes = require("./routes/seed");

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(morgan("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use("/api/health", healthRoutes);
app.use("/api/users", usersRoutes);
app.use("/api/events", eventsRoutes);
app.use("/api/seed", seedRoutes);

// Root route
app.get("/", (req, res) => {
  res.json({
    message: "Welcome to SaveLife API",
    version: "1.0.0",
    endpoints: {
      health: "/api/health",
      users: "/api/users",
      events: "/api/events",
      seed: "/api/seed",
    },
  });
});

// Start server
const start = async () => {
  try {
    await connectDB();
    app.listen(PORT, "0.0.0.0", () => {
      console.log(`🚀 Server running on http://localhost:${PORT}`);
    });
  } catch (err) {
    console.error("❌ Failed to start server:", err.message);
    process.exit(1);
  }
};

start();
